from __future__ import annotations

import base64
import re
from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO
from typing import Literal

from pypdf import PdfReader

from backend.schemas.historico_funcional_schema import (
    HistoricoFuncionalEventoResponse,
    HistoricoFuncionalResponse,
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
    status: Literal["cumprindo", "atrasado", "nao_aplicavel"]
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


def _adicionar_anos(data_base: date, anos: int) -> date:
    try:
        return data_base.replace(year=data_base.year + anos)
    except ValueError:
        return data_base.replace(year=data_base.year + anos, day=28)


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


def _parsear_bloco_secao(tipo: str, descricao: str, bloco: str) -> BlocoHistorico:
    bloco = re.sub(r"\s+", " ", bloco).strip()

    if tipo in {"nomeacao", "substituicao"}:
        padrao = re.compile(
            r"(?P<cargo>.+?)\s+(?P<simbolo>[A-Z]{2,3}\d?)\s+(?P<nivel>[IVX]+)\s+(?P<grau>[A-Z])\s+"
            r"(?P<orgao>.+?)\s+(?P<data1>\d{2}/\d{2}/\d{4})\s+(?P<data2>\d{2}/\d{2}/\d{4})\s+"
            r"(?P<data3>\d{2}/\d{2}/\d{4})\s+(?P<legislacao>.+)$"
        )
        match = padrao.search(bloco)
        if not match:
            raise ValueError(f"Nao foi possivel interpretar o bloco: {descricao}")

        data_publicacao = _parsear_data(match.group("data1"))
        data_posse = _parsear_data(match.group("data2"))
        data_exercicio = _parsear_data(match.group("data3"))
    else:
        padrao = re.compile(
            r"(?P<cargo>.+?)\s+(?P<simbolo>[A-Z]{2,3}\d?)\s+(?P<nivel>[IVX]+)\s+(?P<grau>[A-Z])\s+"
            r"(?P<orgao>.+?)\s+(?P<data1>\d{2}/\d{2}/\d{4})\s+(?P<data2>\d{2}/\d{2}/\d{4})\s+"
            r"(?P<legislacao>.+)$"
        )
        match = padrao.search(bloco)
        if not match:
            raise ValueError(f"Nao foi possivel interpretar o bloco: {descricao}")

        data_publicacao = _parsear_data(match.group("data1"))
        data_posse = _parsear_data(match.group("data2"))
        data_exercicio = data_posse

    cargo = match.group("cargo").strip()
    simbolo = match.group("simbolo").strip()
    nivel = match.group("nivel").strip()
    grau = match.group("grau").strip()
    orgao = match.group("orgao").strip()
    legislacao = match.group("legislacao").strip()

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

    for bloco in blocos:
        if bloco.tipo == "nomeacao":
            referencia_progressao = bloco.data_exercicio
            referencia_promocao = bloco.data_exercicio
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
            atraso = max((bloco.data_exercicio - data_prevista).days, 0)
            status = "atrasado" if atraso > 0 else "cumprindo"
            referencia_progressao = bloco.data_exercicio
        elif bloco.tipo == "promocao":
            data_prevista = _adicionar_anos(referencia_promocao or bloco.data_exercicio, 5)
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
) -> tuple[HistoricoFuncionalResponse, str]:
    texto = extrair_texto_pdf(conteudo_pdf)
    nome, masp, cpf, data_emissao = _extrair_cabecalho(texto)
    blocos = _extrair_blocos(texto)
    if not blocos:
        raise ValueError("Nao foi possivel localizar os blocos do historico funcional.")

    eventos = _gerar_eventos(blocos)
    ultimo_evento = eventos[-1]
    nomeacao = next((evento for evento in eventos if evento.tipo == "nomeacao"), None)
    if nomeacao is None:
        raise ValueError("Nao foi possivel identificar a admissao inicial.")

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

    proxima_progressao_prevista = _proximo_marco(eventos, "progressao", nomeacao.data_efetiva)
    proxima_promocao_prevista = _proximo_marco(eventos, "promocao", nomeacao.data_efetiva)

    resposta = HistoricoFuncionalResponse(
        historico_id=0,
        usuario_id=usuario_id,
        arquivo_nome=arquivo_nome,
        nome=nome,
        masp=masp,
        cpf=cpf,
        data_emissao=data_emissao,
        data_nascimento=data_nascimento,
        data_posse=nomeacao.data_posse,
        data_exercicio=nomeacao.data_exercicio,
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
