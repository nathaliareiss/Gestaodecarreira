from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO
from typing import Literal

import pandas as pd
from pypdf import PdfReader

from backend.schemas.historico_funcional_schema import (
    AfastamentoPeriodoResponse,
    AfastamentoResumoResponse,
    HistoricoFuncionalEventoResponse,
    HistoricoFuncionalResponse,
    HistoricoFuncionalResumoGraficoResponse,
)

SECAO_NOMEOACAO_PREFIXOS = ("Efetivo-Nomeado",)
SECAO_PROGRESSAO_PREFIXOS = ("Progressão",)
SECAO_PROMOCAO_PREFIXOS = ("Promoção",)
SECAO_SUBSTITUICAO_PREFIXOS = ("Substituição",)

ROMANOS_VALIDOS = {
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
}


@dataclass(frozen=True, slots=True)
class EventoHistorico:
    tipo: Literal["nomeacao", "progressao", "promocao", "substituicao"]
    descricao: str
    cargo: str
    simbolo: str
    nivel: str
    grau: str
    data_publicacao: date
    data_efetiva: date
    data_prevista: date | None
    status: Literal["cumprindo", "atrasado", "nao_aplicavel", "estagio_probatorio"]
    atraso_dias: int


@dataclass(frozen=True, slots=True)
class BlocoHistorico:
    tipo: Literal["nomeacao", "progressao", "promocao", "substituicao"]
    descricao: str
    cargo: str
    simbolo: str
    nivel: str
    grau: str
    orgao: str
    data_publicacao: date
    data_posse: date
    data_exercicio: date
    legislacao: str


@dataclass(frozen=True, slots=True)
class AfastamentoPeriodo:
    tipo: Literal[
        "aguardando_resultado_conclusivo_de_exame_pericial",
        "licenca_para_tratamento_de_saude",
    ]
    data_inicio: date
    data_fim: date
    total_dias: int
    legislacao: str | None
    publicacao: date | None


def decodificar_arquivo_base64(conteudo_base64: str) -> bytes:
    if "," in conteudo_base64:
        conteudo_base64 = conteudo_base64.split(",", 1)[1]

    try:
        return base64.b64decode(conteudo_base64, validate=True)
    except Exception as exc:
        raise ValueError("Arquivo PDF invalido ou corrompido.") from exc


def _limpar_linhas(texto: str) -> list[str]:
    linhas = []
    for linha in texto.splitlines():
        limpa = re.sub(r"\s+", " ", linha).strip()
        if limpa:
            linhas.append(limpa)
    return linhas


def _parsear_data(texto: str) -> date:
    dia, mes, ano = map(int, texto.split("/"))
    return date(ano, mes, dia)


def _encontrar_datas(texto: str) -> list[date]:
    datas: list[date] = []
    for valor in re.findall(r"\d{2}/\d{2}/\d{4}", texto):
        try:
            datas.append(_parsear_data(valor))
        except ValueError:
            continue
    return datas


def _escolher_token(tokens: list[str], padrao: str, inicio: int = 0) -> int | None:
    for indice in range(inicio, len(tokens)):
        if re.fullmatch(padrao, tokens[indice]):
            return indice
    return None


def _limpar_rotulo_bloco(texto: str, descricao: str, tipo: str) -> tuple[str, str, str, str, str]:
    texto = re.sub(r"\s+", " ", texto).strip()
    primeira_data = re.search(r"\d{2}/\d{2}/\d{4}", texto)
    if primeira_data is None:
        raise ValueError(f"Nao foi possivel interpretar o bloco: {descricao}")

    prefixo = texto[: primeira_data.start()].strip()
    sufixo = texto[primeira_data.start() :].strip()
    prefixo = re.sub(
        r"\b(Cargo/Função|Cargo/Funcao|Símbolo|Simbolo|NívelGrau|Nível|Nivel|Grau|Órgão/Entidade|Orgão/Entidade|Publicação|Publicacao|Posse|Exercício|Exercicio|Legislação|Legislacao|Vigência|Vigencia)\b",
        " ",
        prefixo,
        flags=re.IGNORECASE,
    )
    prefixo = re.sub(r"\s+", " ", prefixo).strip()
    datas = _encontrar_datas(texto)
    if len(datas) < 2:
        raise ValueError(f"Nao foi possivel interpretar o bloco: {descricao}")

    tokens = prefixo.split()
    simbolo_idx = _escolher_token(tokens, r"[A-Z]{2,3}\d?")
    if simbolo_idx is None:
        raise ValueError(f"Nao foi possivel interpretar o bloco: {descricao}")

    nivel_idx = _escolher_token(tokens, r"[IVX]+", simbolo_idx + 1)
    if nivel_idx is None:
        raise ValueError(f"Nao foi possivel interpretar o bloco: {descricao}")

    grau_idx = _escolher_token(tokens, r"[A-Z]", nivel_idx + 1)
    if grau_idx is None:
        raise ValueError(f"Nao foi possivel interpretar o bloco: {descricao}")

    cargo = " ".join(tokens[:simbolo_idx]).strip() or descricao
    simbolo = tokens[simbolo_idx].strip()
    nivel = tokens[nivel_idx].strip()
    grau = tokens[grau_idx].strip()
    orgao = " ".join(tokens[grau_idx + 1 :]).strip()

    if tipo in {"nomeacao", "substituicao"}:
        data_publicacao = datas[0]
        data_posse = datas[1]
        data_exercicio = datas[2] if len(datas) > 2 else datas[1]
    else:
        data_publicacao = datas[0]
        data_posse = datas[1]
        data_exercicio = datas[1]

    # Usa o sufixo apenas como legislacao quando o padrao rigido falhar.
    legislacao = sufixo
    return cargo, simbolo, nivel, grau, orgao, data_publicacao, data_posse, data_exercicio, legislacao


def _adicionar_anos(data_base: date, anos: int) -> date:
    try:
        return data_base.replace(year=data_base.year + anos)
    except ValueError:
        return data_base.replace(year=data_base.year + anos, day=28)


def _fim_estagio_probatorio(data_exercicio: date) -> date:
    return _adicionar_anos(data_exercicio, 3)


def _e_linha_de_secao(linha: str) -> bool:
    return linha.startswith(
        (
            *SECAO_NOMEOACAO_PREFIXOS,
            *SECAO_PROGRESSAO_PREFIXOS,
            *SECAO_PROMOCAO_PREFIXOS,
            *SECAO_SUBSTITUICAO_PREFIXOS,
        )
    )


def _tipo_secao(linha: str) -> Literal["nomeacao", "progressao", "promocao", "substituicao"]:
    if linha.startswith(SECAO_NOMEOACAO_PREFIXOS):
        return "nomeacao"
    if linha.startswith(SECAO_PROMOCAO_PREFIXOS):
        return "promocao"
    if linha.startswith(SECAO_SUBSTITUICAO_PREFIXOS):
        return "substituicao"
    return "progressao"


TIPOS_AFASTAMENTO = {
    "Aguardando Resultado Conclusivo de Exame Pericial": "aguardando_resultado_conclusivo_de_exame_pericial",
    "Licença para Tratamento de Saúde": "licenca_para_tratamento_de_saude",
}


def _normalizar_sem_acentos(texto: str) -> str:
    import unicodedata

    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caractere)
    ).lower()


TIPOS_AFASTAMENTO_NORMALIZADOS: dict[str, str] = {}
for _titulo_afastamento_original, _tipo_afastamento in TIPOS_AFASTAMENTO.items():
    _chave_normalizada = re.sub(r"\s+", " ", _titulo_afastamento_original).strip().lower()
    TIPOS_AFASTAMENTO_NORMALIZADOS[_chave_normalizada] = _tipo_afastamento
    TIPOS_AFASTAMENTO_NORMALIZADOS[_normalizar_sem_acentos(_chave_normalizada)] = _tipo_afastamento


def _tipo_afastamento_linha(linha: str) -> Literal[
    "aguardando_resultado_conclusivo_de_exame_pericial",
    "licenca_para_tratamento_de_saude",
] | None:
    normalizada = re.sub(r"\s+", " ", linha).strip().lower()
    if normalizada in TIPOS_AFASTAMENTO_NORMALIZADOS:
        return TIPOS_AFASTAMENTO_NORMALIZADOS[normalizada]  # type: ignore[return-value]

    sem_acentos = re.sub(r"\s+", " ", _normalizar_sem_acentos(linha)).strip()
    return TIPOS_AFASTAMENTO_NORMALIZADOS.get(sem_acentos)  # type: ignore[return-value]


def _titulo_afastamento(tipo: str) -> str:
    if tipo == "aguardando_resultado_conclusivo_de_exame_pericial":
        return "Aguardando Resultado Conclusivo de Exame Pericial"
    return "Licença para Tratamento de Saúde"


def _eh_linha_auxiliar_afastamento(linha: str) -> bool:
    linha_normalizada = _normalizar_sem_acentos(re.sub(r"\s+", " ", linha).strip())
    return any(
        trecho in linha_normalizada
        for trecho in (
            "portal do servidor",
            "afastamentos--consultar",
            "cidade administrativa",
            "termos de uso",
            "politica de privacidade",
            "menu > meu espaco",
        )
    ) or bool(re.fullmatch(r"\d{2}/\d{2}/\d{4},\s*\d{2}:\d{2}\s+portal do servidor", linha_normalizada))


def _eh_linha_cabecalho_afastamento(linha: str) -> bool:
    return _normalizar_sem_acentos(re.sub(r"\s+", " ", linha).strip()) == "periodo total de dias legislacao publicacao"


def _limpar_linhas_afastamentos(texto: str) -> list[str]:
    linhas = []
    for linha in texto.splitlines():
        limpa = re.sub(r"\s+", " ", linha).strip()
        if limpa and not _eh_linha_auxiliar_afastamento(limpa):
            linhas.append(limpa)
    return linhas


def _parsear_afastamento_bloco(tipo: str, bloco: str) -> AfastamentoPeriodo:
    bloco = re.sub(r"\s+", " ", bloco).strip()
    datas = re.findall(r"\d{2}/\d{2}/\d{4}", bloco)
    if len(datas) < 2:
        raise ValueError(f"Nao foi possivel interpretar o bloco de afastamento: {_titulo_afastamento(tipo)}")

    data_inicio = _parsear_data(datas[0])
    data_fim = _parsear_data(datas[1])

    pos_segunda_data = bloco.find(datas[1]) + len(datas[1])
    resto = bloco[pos_segunda_data:].strip()
    total_match = re.search(r"\b(\d+)\b", resto)
    if total_match is None:
        raise ValueError(f"Nao foi possivel interpretar o bloco de afastamento: {_titulo_afastamento(tipo)}")

    total_dias = int(total_match.group(1))
    resto = resto[total_match.end() :].strip()

    publicacao: date | None = None
    legislacao: str | None = None
    if resto:
        publicacao_match = re.search(r"\d{2}/\d{2}/\d{4}", resto)
        if publicacao_match:
            legislacao_texto = resto[: publicacao_match.start()].strip()
            if legislacao_texto:
                legislacao = legislacao_texto
            publicacao = _parsear_data(publicacao_match.group(0))
        else:
            legislacao = resto or None

    return AfastamentoPeriodo(
        tipo=tipo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        total_dias=total_dias,
        legislacao=legislacao,
        publicacao=publicacao,
    )


def extrair_afastamentos_pdf(conteudo_pdf: bytes) -> list[AfastamentoPeriodo]:
    texto = extrair_texto_pdf(conteudo_pdf)
    linhas = _limpar_linhas_afastamentos(texto)
    afastamentos: list[AfastamentoPeriodo] = []
    i = 0

    while i < len(linhas):
        tipo = _tipo_afastamento_linha(linhas[i])
        if tipo is None:
            i += 1
            continue

        i += 1
        bloco_linhas: list[str] = []
        while i < len(linhas):
            proximo_tipo = _tipo_afastamento_linha(linhas[i])
            if proximo_tipo is not None:
                break
            if not _eh_linha_cabecalho_afastamento(linhas[i]):
                bloco_linhas.append(linhas[i])
            i += 1

        bloco_texto = " ".join(bloco_linhas)
        if bloco_texto:
            afastamentos.append(_parsear_afastamento_bloco(tipo, bloco_texto))

    return afastamentos


def analisar_afastamentos_pdf(
    conteudo_pdf: bytes,
) -> tuple[list[AfastamentoPeriodo], AfastamentoResumoResponse]:
    afastamentos = extrair_afastamentos_pdf(conteudo_pdf)
    resumo_afastamentos = _montar_resumo_afastamentos(afastamentos)
    return afastamentos, resumo_afastamentos


def _montar_resumo_afastamentos(afastamentos: list[AfastamentoPeriodo]) -> AfastamentoResumoResponse:
    if not afastamentos:
        return AfastamentoResumoResponse(
            periodos_totais=0,
            dias_totais=0,
            dias_por_tipo={},
            periodos_por_tipo={},
        )

    df = pd.DataFrame(
        [
            {
                "tipo": afastamento.tipo,
                "total_dias": afastamento.total_dias,
            }
            for afastamento in afastamentos
        ]
    )

    return AfastamentoResumoResponse(
        periodos_totais=len(afastamentos),
        dias_totais=int(df["total_dias"].sum()),
        dias_por_tipo={str(chave): int(valor) for chave, valor in df.groupby("tipo")["total_dias"].sum().to_dict().items()},
        periodos_por_tipo={str(chave): int(valor) for chave, valor in df.groupby("tipo").size().to_dict().items()},
    )


def _parsear_bloco_secao(tipo: str, descricao: str, bloco: str) -> BlocoHistorico:
    bloco = re.sub(r"\s+", " ", bloco).strip()

    if tipo in {"nomeacao", "substituicao"}:
        padrao = re.compile(
            r"(?P<cargo>.+?)\s+(?P<simbolo>[A-Z]{2,3}\d?)\s+(?P<nivel>[IVX]+)\s+(?P<grau>[A-Z])\s+"
            r"(?P<orgao>.+?)\s+(?P<data1>\d{2}/\d{2}/\d{4})\s+(?P<data2>\d{2}/\d{2}/\d{4})\s+"
            r"(?P<data3>\d{2}/\d{2}/\d{4})\s+(?P<legislacao>.+)$"
        )
        match = padrao.search(bloco)
        if match:
            data_publicacao = _parsear_data(match.group("data1"))
            data_posse = _parsear_data(match.group("data2"))
            data_exercicio = _parsear_data(match.group("data3"))
        else:
            (
                cargo,
                simbolo,
                nivel,
                grau,
                orgao,
                data_publicacao,
                data_posse,
                data_exercicio,
                legislacao,
            ) = _limpar_rotulo_bloco(bloco, descricao, tipo)
            return BlocoHistorico(
                tipo=tipo,
                descricao=descricao,
                cargo=cargo,
                simbolo=simbolo,
                nivel=nivel,
                grau=grau,
                orgao=orgao,
                data_publicacao=data_publicacao,
                data_posse=data_posse,
                data_exercicio=data_exercicio,
                legislacao=legislacao,
            )
    else:
        padrao = re.compile(
            r"(?P<cargo>.+?)\s+(?P<simbolo>[A-Z]{2,3}\d?)\s+(?P<nivel>[IVX]+)\s+(?P<grau>[A-Z])\s+"
            r"(?P<orgao>.+?)\s+(?P<data1>\d{2}/\d{2}/\d{4})\s+(?P<data2>\d{2}/\d{2}/\d{4})\s+"
            r"(?P<legislacao>.+)$"
        )
        match = padrao.search(bloco)
        if match:
            data_publicacao = _parsear_data(match.group("data1"))
            data_posse = _parsear_data(match.group("data2"))
            data_exercicio = data_posse
        else:
            (
                cargo,
                simbolo,
                nivel,
                grau,
                orgao,
                data_publicacao,
                data_posse,
                data_exercicio,
                legislacao,
            ) = _limpar_rotulo_bloco(bloco, descricao, tipo)
            return BlocoHistorico(
                tipo=tipo,
                descricao=descricao,
                cargo=cargo,
                simbolo=simbolo,
                nivel=nivel,
                grau=grau,
                orgao=orgao,
                data_publicacao=data_publicacao,
                data_posse=data_posse,
                data_exercicio=data_exercicio,
                legislacao=legislacao,
            )

    if match:
        cargo = match.group("cargo").strip()
        simbolo = match.group("simbolo").strip()
        nivel = match.group("nivel").strip()
        grau = match.group("grau").strip()
        orgao = match.group("orgao").strip()
        legislacao = match.group("legislacao").strip()
    else:
        partes = bloco.split(" ")
        cargo = descricao
        simbolo = next((parte for parte in partes if re.fullmatch(r"[A-Z]{2,3}\d?", parte)), "")
        nivel = next((parte for parte in partes if re.fullmatch(r"[IVX]+", parte)), "")
        grau = next((parte for parte in partes if re.fullmatch(r"[A-Z]", parte)), "")
        orgao = ""
        legislacao = bloco

    return BlocoHistorico(
        tipo=tipo,
        descricao=descricao,
        cargo=cargo,
        simbolo=simbolo,
        nivel=nivel,
        grau=grau,
        orgao=orgao,
        data_publicacao=data_publicacao,
        data_posse=data_posse,
        data_exercicio=data_exercicio,
        legislacao=legislacao,
    )


def extrair_texto_pdf(conteudo_pdf: bytes) -> str:
    leitor = PdfReader(BytesIO(conteudo_pdf))
    textos = []
    for pagina in leitor.pages:
        textos.append(pagina.extract_text() or "")
    return "\n".join(textos)


def _extrair_cabecalho(texto: str) -> tuple[str, str, str | None, date | None]:
    nome_match = re.search(r"Nome:\s*(.*?)\s+MASP:\s*([0-9\-]+)", texto)
    cpf_match = re.search(r"CPF:\s*([0-9\.\-]+)", texto)
    emissao_match = re.search(r"Data de Emissão:\s*(\d{2}/\d{2}/\d{4})", texto)

    if not nome_match:
        raise ValueError("Nao foi possivel encontrar o nome no PDF.")

    nome = nome_match.group(1).strip()
    masp = nome_match.group(2).strip()
    cpf = cpf_match.group(1).strip() if cpf_match else None
    data_emissao = _parsear_data(emissao_match.group(1)) if emissao_match else None
    return nome, masp, cpf, data_emissao


def _extrair_blocos(texto: str) -> list[BlocoHistorico]:
    linhas = _limpar_linhas(texto)
    blocos: list[BlocoHistorico] = []
    i = 0

    while i < len(linhas):
        linha = linhas[i]
        if not _e_linha_de_secao(linha):
            i += 1
            continue

        tipo = _tipo_secao(linha)
        descricao = linha
        i += 1

        while i < len(linhas) and linhas[i].startswith("Cargo/Função"):
            i += 1

        bloco_linhas: list[str] = []
        while i < len(linhas) and not _e_linha_de_secao(linhas[i]):
            if linhas[i] not in {
                "Cargo/Função Símbolo Nível Grau Órgão/Entidade Publicação Posse Exercício Legislação",
                "Cargo/Função Símbolo Nível Grau Órgão/Entidade Publicação Vigência Legislação",
            }:
                bloco_linhas.append(linhas[i])
            i += 1

        bloco_texto = " ".join(bloco_linhas)
        if bloco_texto:
            blocos.append(_parsear_bloco_secao(tipo, descricao, bloco_texto))

    return blocos


def _gerar_eventos(blocos: list[BlocoHistorico]) -> list[EventoHistorico]:
    eventos: list[EventoHistorico] = []
    referencia_progressao: date | None = None
    referencia_promocao: date | None = None
    fim_estagio_probatorio: date | None = None

    for bloco in blocos:
        if bloco.tipo == "nomeacao":
            fim_estagio_probatorio = _fim_estagio_probatorio(bloco.data_exercicio)
            referencia_progressao = fim_estagio_probatorio
            referencia_promocao = fim_estagio_probatorio
            eventos.append(
                EventoHistorico(
                    tipo="nomeacao",
                    descricao=bloco.descricao,
                    cargo=bloco.cargo,
                    simbolo=bloco.simbolo,
                    nivel=bloco.nivel,
                    grau=bloco.grau,
                    data_publicacao=bloco.data_publicacao,
                    data_efetiva=bloco.data_exercicio,
                    data_prevista=None,
                    status="nao_aplicavel",
                    atraso_dias=0,
                )
            )
            continue

        if bloco.tipo == "progressao":
            data_prevista = _adicionar_anos(referencia_progressao or bloco.data_exercicio, 2)
            if fim_estagio_probatorio is not None and bloco.data_exercicio <= fim_estagio_probatorio:
                data_prevista = fim_estagio_probatorio
                atraso = 0
                status = "estagio_probatorio"
            else:
                atraso = max((bloco.data_exercicio - data_prevista).days, 0)
                status = "atrasado" if atraso > 0 else "cumprindo"
                referencia_progressao = bloco.data_exercicio
        elif bloco.tipo == "promocao":
            data_prevista = _adicionar_anos(referencia_promocao or bloco.data_exercicio, 5)
            if fim_estagio_probatorio is not None and bloco.data_exercicio <= fim_estagio_probatorio:
                data_prevista = fim_estagio_probatorio
                atraso = 0
                status = "estagio_probatorio"
            else:
                atraso = max((bloco.data_exercicio - data_prevista).days, 0)
                status = "atrasado" if atraso > 0 else "cumprindo"
                referencia_promocao = bloco.data_exercicio
        else:
            data_prevista = None
            atraso = 0
            status = "nao_aplicavel"

        eventos.append(
            EventoHistorico(
                tipo=bloco.tipo,
                descricao=bloco.descricao,
                cargo=bloco.cargo,
                simbolo=bloco.simbolo,
                nivel=bloco.nivel,
                grau=bloco.grau,
                data_publicacao=bloco.data_publicacao,
                data_efetiva=bloco.data_exercicio,
                data_prevista=data_prevista,
                status=status,
                atraso_dias=atraso,
            )
        )

    return eventos


def _cronometro_ate_aposentadoria(
    data_nascimento: date,
    data_exercicio: date,
    anos_clt_averbados: int,
) -> tuple[date, date, date, int, int, float, float]:
    anos_creditados = min(max(anos_clt_averbados, 0), 10)
    data_aposentadoria_por_carreira = _adicionar_anos(
        data_exercicio,
        max(25 - anos_creditados, 0),
    )
    data_aposentadoria_por_idade = _adicionar_anos(data_nascimento, 50)
    data_aposentadoria_prevista = max(
        data_aposentadoria_por_carreira,
        data_aposentadoria_por_idade,
    )
    hoje = date.today()
    dias_trabalhados = max((hoje - data_exercicio).days, 0)
    dias_totais = max((data_aposentadoria_prevista - data_exercicio).days, 1)
    percentual_trabalhado = min((dias_trabalhados / dias_totais) * 100, 100)
    percentual_restante = max(100 - percentual_trabalhado, 0)
    return (
        data_aposentadoria_por_carreira,
        data_aposentadoria_por_idade,
        data_aposentadoria_prevista,
        dias_trabalhados,
        dias_totais,
        percentual_trabalhado,
        percentual_restante,
    )


def _montar_resumo_grafico(
    eventos: list[EventoHistorico],
    dias_trabalhados: int,
    dias_totais: int,
    percentual_trabalhado: float,
    percentual_restante: float,
) -> HistoricoFuncionalResumoGraficoResponse:
    if eventos:
        df = pd.DataFrame(
            [
                {
                    "tipo": evento.tipo,
                    "status": evento.status,
                }
                for evento in eventos
            ]
        )
        eventos_por_status = {
            str(chave): int(valor) for chave, valor in df.groupby("status").size().to_dict().items()
        }
        eventos_por_tipo = {
            str(chave): int(valor) for chave, valor in df.groupby("tipo").size().to_dict().items()
        }
    else:
        eventos_por_status = {}
        eventos_por_tipo = {}

    return HistoricoFuncionalResumoGraficoResponse(
        tempo_trabalhado_dias=dias_trabalhados,
        tempo_restante_dias=max(dias_totais - dias_trabalhados, 0),
        percentual_trabalhado=percentual_trabalhado,
        percentual_restante=percentual_restante,
        eventos_totais=len(eventos),
        eventos_por_status=eventos_por_status,
        eventos_por_tipo=eventos_por_tipo,
    )


def _proximo_marco(eventos: list[EventoHistorico], tipo: str, base: date) -> date:
    data_referencia = base
    for evento in eventos:
        if evento.tipo == tipo:
            data_referencia = evento.data_efetiva

    incremento = 2 if tipo == "progressao" else 5
    return _adicionar_anos(data_referencia, incremento)


def analisar_historico_funcional(
    conteudo_pdf: bytes,
    arquivo_nome: str,
    usuario_id: int | None,
    data_nascimento: date,
    anos_clt_averbados: int,
    conteudo_afastamentos_pdf: bytes | None = None,
    arquivo_afastamentos_nome: str | None = None,
) -> tuple[HistoricoFuncionalResponse, str]:
    texto = extrair_texto_pdf(conteudo_pdf)
    nome, masp, cpf, data_emissao = _extrair_cabecalho(texto)
    blocos = _extrair_blocos(texto)
    if not blocos:
        raise ValueError("Nao foi possivel localizar os blocos do historico funcional.")

    eventos = _gerar_eventos(blocos)
    ultimo_evento = eventos[-1]
    nomeacao = next((evento for evento in eventos if evento.tipo == "nomeacao"), None)
    nomeacao_bloco = next((bloco for bloco in blocos if bloco.tipo == "nomeacao"), None)
    if nomeacao is None:
        raise ValueError("Nao foi possivel identificar a admissao inicial.")
    if nomeacao_bloco is None:
        raise ValueError("Nao foi possivel localizar os dados da admissao inicial.")

    inicio_contagem_progressao = _fim_estagio_probatorio(nomeacao.data_efetiva)

    (
        data_aposentadoria_por_carreira,
        data_aposentadoria_por_idade,
        data_aposentadoria_prevista,
        dias_trabalhados,
        dias_totais,
        percentual_trabalhado,
        percentual_restante,
    ) = _cronometro_ate_aposentadoria(
        data_nascimento=data_nascimento,
        data_exercicio=nomeacao.data_efetiva,
        anos_clt_averbados=anos_clt_averbados,
    )

    proxima_progressao_prevista = _proximo_marco(eventos, "progressao", inicio_contagem_progressao)
    proxima_promocao_prevista = _proximo_marco(eventos, "promocao", inicio_contagem_progressao)
    resumo_grafico = _montar_resumo_grafico(
        eventos=eventos,
        dias_trabalhados=dias_trabalhados,
        dias_totais=dias_totais,
        percentual_trabalhado=percentual_trabalhado,
        percentual_restante=percentual_restante,
    )

    afastamentos: list[AfastamentoPeriodo] = []
    resumo_afastamentos: AfastamentoResumoResponse | None = None
    if conteudo_afastamentos_pdf is not None:
        afastamentos = extrair_afastamentos_pdf(conteudo_afastamentos_pdf)
        resumo_afastamentos = _montar_resumo_afastamentos(afastamentos)

    resposta = HistoricoFuncionalResponse(
        historico_id=0,
        usuario_id=usuario_id,
        arquivo_nome=arquivo_nome,
        nome=nome,
        masp=masp,
        cpf=cpf,
        data_emissao=data_emissao,
        data_nascimento=data_nascimento,
        data_posse=nomeacao_bloco.data_posse,
        data_exercicio=nomeacao_bloco.data_exercicio,
        cargo_atual=ultimo_evento.cargo,
        simbolo_atual=ultimo_evento.simbolo,
        nivel_atual=ultimo_evento.nivel,
        grau_atual=ultimo_evento.grau,
        tempo_clt_averbado_anos=anos_clt_averbados,
        tempo_clt_creditado_anos=min(max(anos_clt_averbados, 0), 10),
        data_aposentadoria_por_carreira=data_aposentadoria_por_carreira,
        data_aposentadoria_por_idade=data_aposentadoria_por_idade,
        data_aposentadoria_prevista=data_aposentadoria_prevista,
        dias_trabalhados=dias_trabalhados,
        dias_totais_ate_aposentadoria=dias_totais,
        percentual_trabalhado=percentual_trabalhado,
        percentual_restante=percentual_restante,
        proxima_progressao_prevista=proxima_progressao_prevista,
        proxima_promocao_prevista=proxima_promocao_prevista,
        resumo_grafico=resumo_grafico,
        afastamentos_arquivo_nome=arquivo_afastamentos_nome,
        afastamentos_resumo=resumo_afastamentos,
        afastamentos=[
            AfastamentoPeriodoResponse(
                tipo=afastamento.tipo,
                data_inicio=afastamento.data_inicio,
                data_fim=afastamento.data_fim,
                total_dias=afastamento.total_dias,
                legislacao=afastamento.legislacao,
                publicacao=afastamento.publicacao,
            )
            for afastamento in afastamentos
        ],
        eventos=[
            HistoricoFuncionalEventoResponse(
                tipo=evento.tipo,
                descricao=evento.descricao,
                cargo=evento.cargo,
                simbolo=evento.simbolo,
                nivel=evento.nivel,
                grau=evento.grau,
                data_publicacao=evento.data_publicacao,
                data_efetiva=evento.data_efetiva,
                data_prevista=evento.data_prevista,
                status=evento.status,
                atraso_dias=evento.atraso_dias,
            )
            for evento in eventos
        ],
    )

    return resposta, texto
