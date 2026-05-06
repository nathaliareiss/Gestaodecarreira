from __future__ import annotations

import re
import unicodedata
from decimal import Decimal

from pypdf import PdfReader

ZERO = Decimal("0.00")

MESES = {
    "JANEIRO": 1,
    "FEVEREIRO": 2,
    "MARCO": 3,
    "ABRIL": 4,
    "MAIO": 5,
    "JUNHO": 6,
    "JULHO": 7,
    "AGOSTO": 8,
    "SETEMBRO": 9,
    "OUTUBRO": 10,
    "NOVEMBRO": 11,
    "DEZEMBRO": 12,
}

MESES_POR_NUMERO = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Marco",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

PADRAO_COMPETENCIA = re.compile(
    r"\b(?:COMPETENCIA|COMPETENCIA\s+REFERENCIA|REFERENCIA)\s*[:\-]?\s*"
    r"(?P<mes>[A-Z0-9]+)\s*/\s*(?P<ano>\d{4})",
    re.IGNORECASE,
)

PADRAO_COMPETENCIA_SIMPLES = re.compile(
    r"\b(?P<mes>[A-Z0-9]+)\s*/\s*(?P<ano>\d{4})",
    re.IGNORECASE,
)

PADRAO_VALOR = r"(?P<valor>-?(?:\d{1,3}(?:\.\d{3})*|\d+),\d{2})"

PADROES_VALORES = {
    "bruto": [
        rf"TOTAL\s+DE\s+VANTAGENS\s*[:\-]?\s*{PADRAO_VALOR}",
        rf"TOTAL\s+VANTAGENS\s*[:\-]?\s*{PADRAO_VALOR}",
        rf"BRUTO\s*[:\-]?\s*{PADRAO_VALOR}",
    ],
    "descontos": [
        rf"TOTAL\s+DE\s+DESCONTOS\s*[:\-]?\s*{PADRAO_VALOR}",
        rf"DESCONTOS\s*[:\-]?\s*{PADRAO_VALOR}",
    ],
    "liquido": [
        rf"(?:VALOR\s+)?LIQUIDO\s*[:\-]?\s*{PADRAO_VALOR}",
    ],
    "vencimento_basico": [
        rf"VENCIMENTO\s+BASICO\s*[:\-]?\s*{PADRAO_VALOR}",
        rf"VENCIMENTO\s+BA[S]ICO\s*[:\-]?\s*{PADRAO_VALOR}",
    ],
    "adicional_desempenho": [
        rf"ADICIONAL\s+DESEMPENHO\s*[:\-]?\s*{PADRAO_VALOR}",
    ],
    "adicional_noturno": [
        rf"ADICIONAL\s+NOTURNO\s*[:\-]?\s*{PADRAO_VALOR}",
    ],
    "irrf": [
        rf"IRRF\s*[:\-]?\s*{PADRAO_VALOR}",
        rf"IMPOSTO\s+DE\s+RENDA\s*[:\-]?\s*{PADRAO_VALOR}",
    ],
    "previdencia": [
        rf"PREVIDENCIA\s*[:\-]?\s*{PADRAO_VALOR}",
    ],
}


def _remover_acentos(texto: str) -> str:
    """Normaliza o texto para facilitar as buscas com regex."""

    normalizado = unicodedata.normalize("NFKD", texto)
    return "".join(char for char in normalizado if not unicodedata.combining(char))


def _extrair_texto_pdf(pdf_path: str) -> str:
    leitor = PdfReader(pdf_path, strict=False)
    partes: list[str] = []

    for pagina in leitor.pages:
        texto = pagina.extract_text() or ""
        partes.append(texto)

    return "\n".join(partes)


def _normalizar_para_busca(texto: str) -> str:
    return _remover_acentos(texto).upper()


def _converter_valor_monetario(valor: str | None) -> Decimal:
    if not valor:
        return ZERO

    texto = valor.strip().replace(".", "").replace(",", ".")
    if texto.startswith("(") and texto.endswith(")"):
        texto = f"-{texto[1:-1]}"

    return Decimal(texto).quantize(ZERO)


def _extrair_por_padroes(texto: str, padroes: list[str]) -> Decimal:
    for padrao in padroes:
        correspondencia = re.search(padrao, texto, flags=re.IGNORECASE | re.MULTILINE)
        if correspondencia:
            return _converter_valor_monetario(correspondencia.group("valor"))

    return ZERO


def _converter_mes_para_numero(mes_bruto: str) -> int | None:
    mes_normalizado = _remover_acentos(mes_bruto).upper()

    if mes_normalizado.isdigit():
        mes = int(mes_normalizado)
        return mes if 1 <= mes <= 12 else None

    return MESES.get(mes_normalizado)


def _extrair_competencia(texto: str) -> tuple[str, int, int]:
    for padrao in (PADRAO_COMPETENCIA, PADRAO_COMPETENCIA_SIMPLES):
        correspondencia = padrao.search(texto)
        if not correspondencia:
            continue

        mes = _converter_mes_para_numero(correspondencia.group("mes"))
        ano = int(correspondencia.group("ano"))
        if mes is None:
            continue

        return f"{MESES_POR_NUMERO[mes]}/{ano}", ano, mes

    return "", 0, 0


def parse_contracheque(pdf_path: str) -> dict[str, Decimal | int | str]:
    texto = _extrair_texto_pdf(pdf_path)
    texto_busca = _normalizar_para_busca(texto)
    competencia, ano, mes = _extrair_competencia(texto_busca)

    # Cada campo monetario usa um conjunto pequeno de padroes para continuar
    # funcionando mesmo quando o contracheque variar levemente de layout.
    return {
        "competencia": competencia,
        "ano": ano,
        "mes": mes,
        "bruto": _extrair_por_padroes(texto_busca, PADROES_VALORES["bruto"]),
        "descontos": _extrair_por_padroes(texto_busca, PADROES_VALORES["descontos"]),
        "liquido": _extrair_por_padroes(texto_busca, PADROES_VALORES["liquido"]),
        "vencimento_basico": _extrair_por_padroes(
            texto_busca, PADROES_VALORES["vencimento_basico"]
        ),
        "adicional_desempenho": _extrair_por_padroes(
            texto_busca, PADROES_VALORES["adicional_desempenho"]
        ),
        "adicional_noturno": _extrair_por_padroes(
            texto_busca, PADROES_VALORES["adicional_noturno"]
        ),
        "irrf": _extrair_por_padroes(texto_busca, PADROES_VALORES["irrf"]),
        "previdencia": _extrair_por_padroes(texto_busca, PADROES_VALORES["previdencia"]),
    }
