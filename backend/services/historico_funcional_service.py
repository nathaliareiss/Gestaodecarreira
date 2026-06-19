from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from io import BytesIO
from typing import Literal

import pandas as pd
import holidays
from pypdf import PdfReader

from backend.logger import logger
from backend.schemas.historico_funcional_schema import (
    AfastamentoPeriodoResponse,
    AfastamentoResumoResponse,
    FeriasPeriodoResponse,
    FeriasResumoResponse,
    HistoricoFuncionalEventoResponse,
    HistoricoFuncionalResponse,
    HistoricoFuncionalResumoGraficoResponse,
    CategoriaPrevidenciaria,
    SexoServidor,
)

SECAO_NOMEOACAO_PREFIXOS = ("Efetivo-Nomeado",)
SECAO_PROGRESSAO_PREFIXOS = ("Progressão",)
SECAO_PROMOCAO_PREFIXOS = ("Promoção",)
SECAO_SUBSTITUICAO_PREFIXOS = ("Substituição",)

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
    mes_ano_afastamento: str
    dias_restantes_ate_pericia: int


@dataclass(frozen=True, slots=True)
class FeriasPeriodo:
    tipo: Literal["regular", "premium"]
    data_inicio: date
    data_fim: date
    dias_contabilizados: int
    dias_corridos: int
    regra_contagem: Literal["dias_uteis", "dias_corridos"]
    observacao: str | None = None


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


def _formatar_mes_ano(data_base: date) -> str:
    return f"{data_base.month:02d}/{data_base.year}"


def _dias_restantes_ate_pericia(data_fim: date) -> int:
    hoje = date.today()
    return max((data_fim - hoje).days, 0)


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


def _data_por_tempo_contribuicao(data_exercicio: date, anos_requeridos: int, anos_clt_averbados: int) -> date:
    anos_creditados = min(max(anos_clt_averbados, 0), 10)
    return _adicionar_anos(data_exercicio, max(anos_requeridos - anos_creditados, 0))


def _dias_contribuicao_em(data_referencia: date, data_exercicio: date, anos_clt_averbados: int) -> int:
    dias_carreira = max((data_referencia - data_exercicio).days, 0)
    dias_clt = min(max(anos_clt_averbados, 0), 10) * 365
    return dias_carreira + dias_clt


def _anos_por_dias(dias: int) -> float:
    return dias / 365.2425


def _meses_desde(inicio: date, fim: date) -> int:
    return max((fim.year - inicio.year) * 12 + (fim.month - inicio.month), 0)


def _pontuacao_exigida_art_146(data_referencia: date, sexo: SexoServidor, professor: bool) -> int:
    if professor:
        base = 81 if sexo == "feminino" else 92
        teto = 92 if sexo == "feminino" else 100
        incremento = max(data_referencia.year - 2020, 0) if data_referencia >= date(2021, 1, 1) else 0
        return min(base + incremento, teto)

    base = 86 if sexo == "feminino" else 97
    teto = 100 if sexo == "feminino" else 105
    incremento = 0
    marco = date(2021, 1, 1)
    if data_referencia >= marco:
        incremento = (_meses_desde(marco, data_referencia) // 15) + 1
    return min(base + incremento, teto)


def _calcular_data_pontos_art_146(
    data_nascimento: date,
    data_exercicio: date,
    anos_clt_averbados: int,
    sexo: SexoServidor,
    categoria_previdenciaria: CategoriaPrevidenciaria,
) -> tuple[date, date, date]:
    professor = categoria_previdenciaria == "professor"
    idade_minima = 51 if professor and sexo == "feminino" else 57 if professor else 56 if sexo == "feminino" else 62
    contribuicao_minima = 25 if professor and sexo == "feminino" else 30 if professor else 30 if sexo == "feminino" else 35
    data_por_idade = _adicionar_anos(data_nascimento, idade_minima)
    data_por_contribuicao = _data_por_tempo_contribuicao(data_exercicio, contribuicao_minima, anos_clt_averbados)
    data_por_servico_publico = _adicionar_anos(data_exercicio, 10)
    data_por_cargo = _adicionar_anos(data_exercicio, 5)
    cursor = max(data_por_idade, data_por_contribuicao, data_por_servico_publico, data_por_cargo)

    for _ in range(365 * 80):
        idade = _anos_por_dias((cursor - data_nascimento).days)
        contribuicao = _anos_por_dias(_dias_contribuicao_em(cursor, data_exercicio, anos_clt_averbados))
        if idade + contribuicao >= _pontuacao_exigida_art_146(cursor, sexo, professor):
            return data_por_contribuicao, data_por_idade, cursor
        cursor += timedelta(days=1)

    return data_por_contribuicao, data_por_idade, cursor


def _calcular_data_pedagio_art_147(
    data_nascimento: date,
    data_exercicio: date,
    anos_clt_averbados: int,
    sexo: SexoServidor,
    categoria_previdenciaria: CategoriaPrevidenciaria,
) -> tuple[date, date, date]:
    professor = categoria_previdenciaria == "professor"
    marco_reforma = date(2020, 9, 14)
    idade_minima = 50 if professor and sexo == "feminino" else 55 if professor else 55 if sexo == "feminino" else 60
    contribuicao_minima = 25 if professor and sexo == "feminino" else 30 if professor else 30 if sexo == "feminino" else 35
    dias_minimos = contribuicao_minima * 365
    dias_em_2020 = _dias_contribuicao_em(marco_reforma, data_exercicio, anos_clt_averbados)
    pedagio = max(dias_minimos - dias_em_2020, 0) // 2
    dias_necessarios = dias_minimos + pedagio
    dias_clt = min(max(anos_clt_averbados, 0), 10) * 365
    data_por_contribuicao = data_exercicio + timedelta(days=max(dias_necessarios - dias_clt, 0))
    data_por_idade = _adicionar_anos(data_nascimento, idade_minima)
    data_prevista = max(data_por_contribuicao, data_por_idade, _adicionar_anos(data_exercicio, 10), _adicionar_anos(data_exercicio, 5))
    return data_por_contribuicao, data_por_idade, data_prevista


def _calcular_data_regra_permanente(
    data_nascimento: date,
    data_exercicio: date,
    anos_clt_averbados: int,
    sexo: SexoServidor,
    categoria_previdenciaria: CategoriaPrevidenciaria,
) -> tuple[date, date, date]:
    if categoria_previdenciaria == "professor":
        idade_minima = 57 if sexo == "feminino" else 60
        contribuicao_minima = 25
        anos_servico = 10
        anos_cargo = 5
    elif categoria_previdenciaria == "seguranca":
        idade_minima = 55
        contribuicao_minima = 30
        anos_servico = 25
        anos_cargo = 25
    elif categoria_previdenciaria == "saude_exposicao":
        idade_minima = 60
        contribuicao_minima = 25
        anos_servico = 10
        anos_cargo = 5
    else:
        idade_minima = 62 if sexo == "feminino" else 65
        contribuicao_minima = 25
        anos_servico = 10
        anos_cargo = 5
    data_por_contribuicao = _data_por_tempo_contribuicao(data_exercicio, contribuicao_minima, anos_clt_averbados)
    data_por_idade = _adicionar_anos(data_nascimento, idade_minima)
    data_prevista = max(
        data_por_contribuicao,
        data_por_idade,
        _adicionar_anos(data_exercicio, anos_servico),
        _adicionar_anos(data_exercicio, anos_cargo),
    )
    return data_por_contribuicao, data_por_idade, data_prevista


def _calcular_data_saude_exposicao_art_149(
    data_nascimento: date,
    data_exercicio: date,
    anos_clt_averbados: int,
) -> tuple[date, date, date]:
    data_por_contribuicao = _data_por_tempo_contribuicao(data_exercicio, 25, anos_clt_averbados)
    data_por_idade = data_exercicio
    data_por_servico_publico = _adicionar_anos(data_exercicio, 20)
    cursor = max(data_por_contribuicao, data_por_servico_publico, _adicionar_anos(data_exercicio, 5))

    for _ in range(365 * 80):
        idade = _anos_por_dias(max((cursor - data_nascimento).days, 0))
        contribuicao = _anos_por_dias(_dias_contribuicao_em(cursor, data_exercicio, anos_clt_averbados))
        exposicao = _anos_por_dias(max((cursor - data_exercicio).days, 0))
        if idade + contribuicao + exposicao >= 86:
            return data_por_contribuicao, data_por_idade, cursor
        cursor += timedelta(days=1)

    return data_por_contribuicao, data_por_idade, cursor


def _cargo_indica_professor(blocos: list[BlocoHistorico]) -> bool:
    texto_cargos = " ".join(f"{bloco.cargo} {bloco.descricao}" for bloco in blocos)
    normalizado = _normalizar_sem_acentos(texto_cargos)
    return any(termo in normalizado for termo in ("professor", "peb", "regente de ensino"))


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


def _ordem_tipo_bloco(tipo: Literal["nomeacao", "progressao", "promocao", "substituicao"]) -> int:
    if tipo == "nomeacao":
        return 0
    if tipo == "progressao":
        return 1
    if tipo == "promocao":
        return 2
    return 3


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
        mes_ano_afastamento=_formatar_mes_ano(data_inicio),
        dias_restantes_ate_pericia=_dias_restantes_ate_pericia(data_fim),
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
    logger.info(
        "Afastamentos analisados",
        extra={"periodos": len(afastamentos)},
    )
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


def _tipo_ferias_linha(linha: str) -> Literal["regular", "premium"] | None:
    normalizada = _normalizar_sem_acentos(re.sub(r"\s+", " ", linha).strip())
    if "ferias" not in normalizada:
        return None
    if "premio" in normalizada:
        return "premium"
    if "regulamentar" in normalizada or "regular" in normalizada:
        return "regular"
    return None


def _contar_dias_uteis(data_inicio: date, data_fim: date) -> int:
    feriados = holidays.country_holidays("BR", subdiv="MG", years=range(data_inicio.year, data_fim.year + 1))
    total = 0
    cursor = data_inicio
    while cursor <= data_fim:
        if cursor.weekday() < 5 and cursor not in feriados:
            total += 1
        cursor += timedelta(days=1)
    return total


def _montar_ferias_periodo(
    tipo: Literal["regular", "premium"],
    data_inicio: date,
    data_fim: date,
    observacao: str | None = None,
) -> FeriasPeriodo:
    if data_fim < data_inicio:
        data_inicio, data_fim = data_fim, data_inicio

    dias_corridos = (data_fim - data_inicio).days + 1
    if tipo == "regular":
        return FeriasPeriodo(
            tipo=tipo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            dias_contabilizados=_contar_dias_uteis(data_inicio, data_fim),
            dias_corridos=dias_corridos,
            regra_contagem="dias_uteis",
            observacao=observacao,
        )

    return FeriasPeriodo(
        tipo=tipo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        dias_contabilizados=dias_corridos,
        dias_corridos=dias_corridos,
        regra_contagem="dias_corridos",
        observacao=observacao,
    )


def extrair_ferias_pdf(conteudo_pdf: bytes) -> list[FeriasPeriodo]:
    texto = extrair_texto_pdf(conteudo_pdf)
    linhas = _limpar_linhas(texto)
    periodos: list[FeriasPeriodo] = []
    vistos: set[tuple[str, date, date]] = set()
    tipo_atual: Literal["regular", "premium"] | None = None
    texto_normalizado = _normalizar_sem_acentos(texto)

    if "ferias regulamentares" in texto_normalizado:
        for linha in linhas:
            match = re.match(
                r"^\d{4}\s+(?P<inicio>\d{2}/\d{2}/\d{4})\s+(?P<retorno_previsto>\d{2}/\d{2}/\d{4})\s+(?P<retorno_efetivo>\d{2}/\d{2}/\d{4}|-)",
                linha,
            )
            if not match:
                continue
            data_inicio = _parsear_data(match.group("inicio"))
            retorno_texto = match.group("retorno_efetivo")
            if retorno_texto == "-":
                retorno_texto = match.group("retorno_previsto")
            data_fim = _parsear_data(retorno_texto) - timedelta(days=1)
            chave = ("regular", data_inicio, data_fim)
            if chave not in vistos:
                vistos.add(chave)
                periodos.append(_montar_ferias_periodo("regular", data_inicio, data_fim, linha))

    if "ferias-premio" in texto_normalizado or "ferias premio" in texto_normalizado:
        texto_compacto = re.sub(r"\s+", " ", texto)
        for match in re.finditer(
            r"(?P<inicio>\d{2}/\d{2}/\d{4})\s*a\s*(?P<fim>\d{2}/\d{2}/\d{4})",
            texto_compacto,
            flags=re.IGNORECASE,
        ):
            data_inicio = _parsear_data(match.group("inicio"))
            data_fim = _parsear_data(match.group("fim"))
            chave = ("premium", data_inicio, data_fim)
            if chave not in vistos:
                vistos.add(chave)
                periodos.append(_montar_ferias_periodo("premium", data_inicio, data_fim, match.group(0)))

    if not periodos:
        for linha in linhas:
            tipo_linha = _tipo_ferias_linha(linha)
            if tipo_linha is not None:
                tipo_atual = tipo_linha

            datas = _encontrar_datas(linha)
            if len(datas) < 2 or tipo_atual is None:
                continue

            for indice in range(0, len(datas) - 1, 2):
                data_inicio = datas[indice]
                data_fim = datas[indice + 1]
                chave = (tipo_atual, data_inicio, data_fim)
                if chave in vistos:
                    continue
                vistos.add(chave)
                periodos.append(_montar_ferias_periodo(tipo_atual, data_inicio, data_fim, linha))

    if not periodos:
        raise ValueError("Nao foi possivel localizar periodos de ferias no PDF.")

    return periodos


def _montar_resumo_ferias(ferias: list[FeriasPeriodo]) -> FeriasResumoResponse:
    if not ferias:
        return FeriasResumoResponse(
            periodos_totais=0,
            dias_totais_usados=0,
            dias_por_tipo={},
            periodos_por_tipo={},
        )

    df = pd.DataFrame(
        [
            {
                "tipo": item.tipo,
                "dias_contabilizados": item.dias_contabilizados,
            }
            for item in ferias
        ]
    )
    hoje = date.today()
    futuras = sorted((item for item in ferias if item.data_inicio >= hoje), key=lambda item: item.data_inicio)
    proxima = futuras[0] if futuras else None

    return FeriasResumoResponse(
        periodos_totais=len(ferias),
        dias_totais_usados=int(df["dias_contabilizados"].sum()),
        dias_por_tipo={
            str(chave): int(valor)
            for chave, valor in df.groupby("tipo")["dias_contabilizados"].sum().to_dict().items()
        },
        periodos_por_tipo={str(chave): int(valor) for chave, valor in df.groupby("tipo").size().to_dict().items()},
        proxima_ferias_inicio=proxima.data_inicio if proxima else None,
        proxima_ferias_fim=proxima.data_fim if proxima else None,
        proxima_ferias_tipo=proxima.tipo if proxima else None,
    )


def analisar_ferias_pdf(
    conteudo_pdf: bytes,
) -> tuple[list[FeriasPeriodo], FeriasResumoResponse]:
    ferias = extrair_ferias_pdf(conteudo_pdf)
    resumo_ferias = _montar_resumo_ferias(ferias)
    logger.info(
        "Ferias analisadas",
        extra={"periodos": len(ferias), "dias_totais": resumo_ferias.dias_totais_usados},
    )
    return ferias, resumo_ferias


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

    blocos_ordenados = sorted(
        blocos,
        key=lambda bloco: (
            bloco.data_exercicio,
            _ordem_tipo_bloco(bloco.tipo),
        ),
    )

    for bloco in blocos_ordenados:
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
    sexo: SexoServidor,
    categoria_previdenciaria: CategoriaPrevidenciaria,
) -> tuple[date, date, date, int, int, float, float]:
    opcoes = [
        _calcular_data_regra_permanente(
            data_nascimento,
            data_exercicio,
            anos_clt_averbados,
            sexo,
            categoria_previdenciaria,
        )
    ]
    if data_exercicio <= date(2020, 9, 14) and categoria_previdenciaria in {"geral", "professor"}:
        opcoes.append(
            _calcular_data_pontos_art_146(
                data_nascimento,
                data_exercicio,
                anos_clt_averbados,
                sexo,
                categoria_previdenciaria,
            )
        )
    if data_exercicio <= date(2020, 9, 14) and categoria_previdenciaria == "saude_exposicao":
        opcoes.append(
            _calcular_data_saude_exposicao_art_149(
                data_nascimento,
                data_exercicio,
                anos_clt_averbados,
            )
        )
        opcoes.append(
            _calcular_data_pedagio_art_147(
                data_nascimento,
                data_exercicio,
                anos_clt_averbados,
                sexo,
                categoria_previdenciaria,
            )
        )

    data_aposentadoria_por_carreira, data_aposentadoria_por_idade, data_aposentadoria_prevista = min(
        opcoes,
        key=lambda item: item[2],
    )
    hoje = date.today()
    dias_trabalhados = _dias_contribuicao_em(hoje, data_exercicio, anos_clt_averbados)
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
    sexo: SexoServidor,
    categoria_previdenciaria: CategoriaPrevidenciaria,
    anos_clt_averbados: int,
    conteudo_afastamentos_pdf: bytes | None = None,
    arquivo_afastamentos_nome: str | None = None,
    conteudo_ferias_pdf: bytes | None = None,
    arquivo_ferias_nome: str | None = None,
) -> tuple[HistoricoFuncionalResponse, str]:
    logger.info(
        "Iniciando analise de historico funcional",
        extra={
            "arquivo_nome": arquivo_nome,
            "usuario_id": usuario_id,
            "possui_afastamentos": conteudo_afastamentos_pdf is not None,
            "possui_ferias": conteudo_ferias_pdf is not None,
        },
    )
    texto = extrair_texto_pdf(conteudo_pdf)
    nome, masp, cpf, data_emissao = _extrair_cabecalho(texto)
    blocos = _extrair_blocos(texto)
    if not blocos:
        raise ValueError("Nao foi possivel localizar os blocos do historico funcional.")
    logger.debug(
        "Blocos do historico identificados",
        extra={"arquivo_nome": arquivo_nome, "blocos": len(blocos)},
    )

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
        sexo=sexo,
        categoria_previdenciaria=categoria_previdenciaria,
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
        logger.info(
            "Historico funcional com afastamentos anexados",
            extra={
                "arquivo_nome": arquivo_nome,
                "arquivo_afastamentos_nome": arquivo_afastamentos_nome,
                "periodos_afastamento": len(afastamentos),
            },
        )

    ferias: list[FeriasPeriodo] = []
    resumo_ferias: FeriasResumoResponse | None = None
    if conteudo_ferias_pdf is not None:
        ferias = extrair_ferias_pdf(conteudo_ferias_pdf)
        resumo_ferias = _montar_resumo_ferias(ferias)
        logger.info(
            "Historico funcional com ferias anexadas",
            extra={
                "arquivo_nome": arquivo_nome,
                "arquivo_ferias_nome": arquivo_ferias_nome,
                "periodos_ferias": len(ferias),
            },
        )

    resposta = HistoricoFuncionalResponse(
        historico_id=0,
        usuario_id=usuario_id,
        arquivo_nome=arquivo_nome,
        nome=nome,
        masp=masp,
        cpf=cpf,
        data_emissao=data_emissao,
        data_nascimento=data_nascimento,
        sexo=sexo,
        categoria_previdenciaria=categoria_previdenciaria,
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
                mes_ano_afastamento=afastamento.mes_ano_afastamento,
                dias_restantes_ate_pericia=afastamento.dias_restantes_ate_pericia,
            )
            for afastamento in afastamentos
        ],
        ferias_arquivo_nome=arquivo_ferias_nome,
        ferias_resumo=resumo_ferias,
        ferias=[
            FeriasPeriodoResponse(
                tipo=item.tipo,
                data_inicio=item.data_inicio,
                data_fim=item.data_fim,
                dias_contabilizados=item.dias_contabilizados,
                dias_corridos=item.dias_corridos,
                regra_contagem=item.regra_contagem,
                observacao=item.observacao,
            )
            for item in ferias
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

    logger.info(
        "Analise concluida",
        extra={
            "arquivo_nome": arquivo_nome,
            "usuario_id": usuario_id,
            "eventos": len(eventos),
            "afastamentos": len(afastamentos),
            "ferias": len(ferias),
        },
    )
    return resposta, texto
