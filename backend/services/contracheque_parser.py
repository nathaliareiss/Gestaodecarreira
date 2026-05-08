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
PADRAO_VALOR_LINHA = re.compile(r"-?(?:\d{1,3}(?:\.\d{3})*|\d+),\d{2}")
PADRAO_TOTAL_BLOCO = re.compile(
    rf"(?P<section>VANTAGENS|DESCONTOS).*?TOTAL:\s*R?\$\s*{PADRAO_VALOR}",
    re.IGNORECASE | re.DOTALL,
)
PADRAO_LIQUIDO_BLOCO = re.compile(
    rf"VALOR\s+A\s+RECEBER\s*R?\$\s*{PADRAO_VALOR}",
    re.IGNORECASE | re.DOTALL,
)
PADRAO_RUBRICA_VALOR_FINAL = re.compile(
    rf"(?P<valor>-?(?:\d{{1,3}}(?:\.\d{{3}})*|\d+),\d{{2}})$",
)

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
        rf"VALOR\s+A\s+RECEBER\s*R?\$\s*{PADRAO_VALOR}",
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

CATEGORIAS_VANTAGEM = (
    "salario_base",
    "ade",
    "adicional_noturno",
    "alimentacao",
    "decimo_terceiro",
    "ferias",
    "retroativo",
    "abono_vestimenta",
    "outros_vantagens",
)

CATEGORIAS_DESCONTO = (
    "previdencia",
    "irrf",
    "emprestimo",
    "saude",
    "associacao",
    "outros_descontos",
)

PADROES_RUBRICAS = [
    (
        "vantagem",
        "salario_base",
        "Vencimento Basico",
        [rf"VENCIMENTO\s+BASICO.*?{PADRAO_VALOR}"],
    ),
    (
        "vantagem",
        "ade",
        "Adicional Desempenho",
        [rf"ADICIONAL\s+DESEMPENHO.*?{PADRAO_VALOR}", rf"\bADE\b.*?{PADRAO_VALOR}"],
    ),
    (
        "vantagem",
        "adicional_noturno",
        "Adicional Noturno",
        [rf"ADICIONAL\s+NOTURNO.*?{PADRAO_VALOR}", rf"ADIC\s+NOT.*?{PADRAO_VALOR}"],
    ),
    (
        "vantagem",
        "alimentacao",
        "Aj.custo/aliment",
        [
            rf"AJ\.?\s*CUSTO\s*/\s*ALIMENT.*?{PADRAO_VALOR}",
            rf"AJUDA\s+DE\s+CUSTO.*?ALIMENT.*?{PADRAO_VALOR}",
            rf"ALIMENTACAO.*?{PADRAO_VALOR}",
        ],
    ),
    (
        "vantagem",
        "decimo_terceiro",
        "Decimo Terceiro",
        [rf"13(?:º|O)?\s+SALARIO.*?{PADRAO_VALOR}", rf"DECIMO\s+TERCEIRO.*?{PADRAO_VALOR}"],
    ),
    (
        "vantagem",
        "ferias",
        "Ferias",
        [rf"\bFERIAS\b.*?{PADRAO_VALOR}", rf"1/3.*?FERIAS.*?{PADRAO_VALOR}"],
    ),
    (
        "vantagem",
        "retroativo",
        "Retroativo",
        [rf"RETROATIV\w*.*?{PADRAO_VALOR}"],
    ),
    (
        "vantagem",
        "abono_vestimenta",
        "Abono Aqu. vestimenta",
        [
            rf"ABONO\s+AQ\.?\s*VESTIMENTA.*?{PADRAO_VALOR}",
            rf"ABONO\s+VESTIMENTA.*?{PADRAO_VALOR}",
            rf"VESTIMENTA.*?{PADRAO_VALOR}",
        ],
    ),
    (
        "desconto",
        "previdencia",
        "Contrib.prev",
        [rf"CONTRIB\.?\s*PREV.*?{PADRAO_VALOR}", rf"PREVIDENCIA.*?{PADRAO_VALOR}"],
    ),
    (
        "desconto",
        "irrf",
        "Imp. Renda Ret.fonte",
        [rf"IRRF.*?{PADRAO_VALOR}", rf"IMP\.\s*RENDA.*?{PADRAO_VALOR}"],
    ),
    (
        "desconto",
        "emprestimo",
        "Emprestimo",
        [
            rf"EMPREST\w*.*?{PADRAO_VALOR}",
            rf"B\.?\s*PAN.*?EMPREST.*?{PADRAO_VALOR}",
        ],
    ),
    (
        "desconto",
        "saude",
        "Saude",
        [rf"SAUDE.*?{PADRAO_VALOR}", rf"COPART\w*.*?{PADRAO_VALOR}"],
    ),
    (
        "desconto",
        "associacao",
        "Associacao",
        [rf"ASSOC\w*.*?{PADRAO_VALOR}"],
    ),
]


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
    return _remover_acentos(texto).upper().strip()


def _normalizar_para_comparacao(texto: str) -> str:
    texto_limpo = _normalizar_para_busca(texto)
    return re.sub(r"[^A-Z0-9]+", " ", texto_limpo).strip()


def _limpar_descricao_rubrica(linha: str) -> str:
    descricao = linha.strip()
    descricao = re.sub(r"^\d+\s+\S+\s+", "", descricao).strip()
    descricao = re.sub(r"\s*[-â€“–]\s*$", "", descricao).strip()
    descricao = re.sub(r"\s+\d+$", "", descricao).strip()
    descricao = re.sub(r"\s+de$", "", descricao, flags=re.IGNORECASE).strip()
    return descricao


def _classificar_rubrica(tipo: str, descricao_original: str) -> str:
    descricao_busca = _normalizar_para_comparacao(descricao_original)

    if tipo == "vantagem":
        if "VENCIMENTO BASICO" in descricao_busca:
            return "salario_base"
        if "ADICIONAL DESEMPENHO" in descricao_busca or re.search(r"\bADE\b", descricao_busca):
            return "ade"
        if "ADICIONAL NOTURNO" in descricao_busca or "ADIC NOT" in descricao_busca:
            return "adicional_noturno"
        if "AJ CUSTO ALIMENT" in descricao_busca or "AJUDA DE CUSTO" in descricao_busca or "ALIMENTAC" in descricao_busca:
            return "alimentacao"
        if "13 SALARIO" in descricao_busca or "DECIMO TERCEIRO" in descricao_busca:
            return "decimo_terceiro"
        if "FERIAS" in descricao_busca:
            return "ferias"
        if "RETROAT" in descricao_busca:
            return "retroativo"
        if "VESTIMENTA" in descricao_busca:
            return "abono_vestimenta"
        return "outros_vantagens"

    if "PREVID" in descricao_busca or "CONTRIB PREV" in descricao_busca:
        return "previdencia"
    if "IRRF" in descricao_busca or "IMPOSTO DE RENDA" in descricao_busca:
        return "irrf"
    if "EMPREST" in descricao_busca or "B PAN" in descricao_busca:
        return "emprestimo"
    if "SAUDE" in descricao_busca or "COPART" in descricao_busca:
        return "saude"
    if "ASSOC" in descricao_busca:
        return "associacao"
    return "outros_descontos"


def _montar_rubrica(tipo: str, descricao_original: str, valor: Decimal) -> dict[str, str | Decimal]:
    categoria_normalizada = _classificar_rubrica(tipo, descricao_original)
    return {
        "tipo": tipo,
        "categoria_normalizada": categoria_normalizada,
        "descricao_original": descricao_original,
        "descricao": descricao_original,
        "valor": valor.quantize(ZERO),
    }


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


def _extrair_ultimo_valor_da_linha(linha: str) -> Decimal:
    valores = PADRAO_VALOR_LINHA.findall(linha)
    if not valores:
        return ZERO

    return _converter_valor_monetario(valores[-1])


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


def _extrair_dados_por_linhas(texto: str) -> dict[str, Decimal]:
    dados = {
        "bruto": ZERO,
        "descontos": ZERO,
        "liquido": ZERO,
        "vencimento_basico": ZERO,
        "adicional_desempenho": ZERO,
        "adicional_noturno": ZERO,
        "irrf": ZERO,
        "previdencia": ZERO,
    }

    estado = None
    for linha_bruta in texto.splitlines():
        linha = _normalizar_para_busca(linha_bruta)
        if not linha:
            continue

        if linha == "VANTAGENS":
            estado = "vantagens"
            continue

        if linha == "DESCONTOS":
            estado = "descontos"
            continue

        if linha.startswith("TOTAL:"):
            valor = _extrair_ultimo_valor_da_linha(linha)
            if estado == "vantagens" and dados["bruto"] == ZERO:
                dados["bruto"] = valor
            elif estado == "descontos" and dados["descontos"] == ZERO:
                dados["descontos"] = valor
            continue

        if "VALOR A RECEBER" in linha:
            dados["liquido"] = _extrair_ultimo_valor_da_linha(linha)
            continue

        if "VENCIMENTO BASICO" in linha:
            dados["vencimento_basico"] = _extrair_ultimo_valor_da_linha(linha)
            continue

        if "ADICIONAL DESEMPENHO" in linha:
            dados["adicional_desempenho"] = _extrair_ultimo_valor_da_linha(linha)
            continue

        if "ADIC NOT" in linha or "ADICIONAL NOTURNO" in linha:
            dados["adicional_noturno"] = _extrair_ultimo_valor_da_linha(linha)
            continue

        if "IMP. RENDA RET.FONTE" in linha or "IMPOSTO DE RENDA" in linha or "IRRF" in linha:
            dados["irrf"] = _extrair_ultimo_valor_da_linha(linha)
            continue

        if "CONTRIB.PREV" in linha or "PREVID" in linha:
            dados["previdencia"] = _extrair_ultimo_valor_da_linha(linha)
            continue

    return dados


def _extrair_total_por_bloco(texto: str, secao: str) -> Decimal:
    correspondencia = re.search(
        rf"{secao}.*?TOTAL:\s*R?\$\s*{PADRAO_VALOR}",
        texto,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not correspondencia:
        return ZERO

    return _converter_valor_monetario(correspondencia.group("valor"))


def _extrair_liquido_por_bloco(texto: str) -> Decimal:
    correspondencia = PADRAO_LIQUIDO_BLOCO.search(texto)
    if not correspondencia:
        return ZERO

    return _converter_valor_monetario(correspondencia.group("valor"))


def parse_contracheque(pdf_path: str) -> dict[str, Decimal | int | str]:
    texto = _extrair_texto_pdf(pdf_path)
    texto_busca = _normalizar_para_busca(texto)
    competencia, ano, mes = _extrair_competencia(texto_busca)
    dados_linhas = _extrair_dados_por_linhas(texto)

    # Cada campo monetario usa um conjunto pequeno de padroes para continuar
    # funcionando mesmo quando o contracheque variar levemente de layout.
    return {
        "competencia": competencia,
        "ano": ano,
        "mes": mes,
        "bruto": _extrair_por_padroes(texto_busca, PADROES_VALORES["bruto"])
        or dados_linhas["bruto"],
        "descontos": _extrair_por_padroes(texto_busca, PADROES_VALORES["descontos"])
        or dados_linhas["descontos"],
        "liquido": _extrair_por_padroes(texto_busca, PADROES_VALORES["liquido"])
        or dados_linhas["liquido"],
        "vencimento_basico": _extrair_por_padroes(
            texto_busca, PADROES_VALORES["vencimento_basico"]
        )
        or dados_linhas["vencimento_basico"],
        "adicional_desempenho": _extrair_por_padroes(
            texto_busca, PADROES_VALORES["adicional_desempenho"]
        )
        or dados_linhas["adicional_desempenho"],
        "adicional_noturno": _extrair_por_padroes(
            texto_busca, PADROES_VALORES["adicional_noturno"]
        )
        or dados_linhas["adicional_noturno"],
        "irrf": _extrair_por_padroes(texto_busca, PADROES_VALORES["irrf"])
        or dados_linhas["irrf"],
        "previdencia": _extrair_por_padroes(texto_busca, PADROES_VALORES["previdencia"])
        or dados_linhas["previdencia"],
    }


def extrair_rubricas_contracheque(pdf_path: str) -> list[dict[str, str | Decimal]]:
    texto = _extrair_texto_pdf(pdf_path)
    rubricas = _extrair_rubricas_do_texto_limpo(texto)
    if rubricas:
        return rubricas

    return _extrair_rubricas_por_padroes(_normalizar_para_busca(texto))


def _extrair_rubricas_do_texto_limpo(texto: str) -> list[dict[str, str | Decimal]]:
    rubricas: list[dict[str, str | Decimal]] = []
    secao: str | None = None

    for linha_bruta in texto.splitlines():
        linha_original = linha_bruta.strip()
        if not linha_original:
            continue

        linha_busca = _normalizar_para_busca(linha_original)
        if linha_busca.startswith("VANTAGENS"):
            secao = "vantagem"
            continue

        if linha_busca.startswith("DESCONTOS"):
            secao = "desconto"
            continue

        if linha_busca.startswith("TOTAL:") or "VALOR A RECEBER" in linha_busca:
            secao = None
            continue

        if secao is None:
            continue

        correspondencia = PADRAO_RUBRICA_VALOR_FINAL.search(linha_original)
        if not correspondencia:
            continue

        descricao = _limpar_descricao_rubrica(
            linha_original[: correspondencia.start("valor")].strip()
        )
        descricao_original = descricao or linha_original

        rubricas.append(
            _montar_rubrica(
                secao,
                descricao_original,
                _converter_valor_monetario(correspondencia.group("valor")),
            )
        )

    return rubricas


def _extrair_rubricas_por_padroes(texto_busca: str) -> list[dict[str, str | Decimal]]:
    rubricas: list[dict[str, str | Decimal]] = []
    for tipo, categoria_normalizada, descricao, padroes_item in PADROES_RUBRICAS:
        for padrao in padroes_item:
            correspondencia = re.search(padrao, texto_busca, flags=re.IGNORECASE | re.DOTALL)
            if not correspondencia:
                continue

            rubrica = _montar_rubrica(
                tipo,
                descricao,
                _converter_valor_monetario(correspondencia.group("valor")),
            )
            rubrica["categoria_normalizada"] = categoria_normalizada
            rubricas.append(rubrica)
            break

    return rubricas


def _extrair_rubricas_do_texto(texto: str) -> list[dict[str, str | Decimal]]:
    rubricas: list[dict[str, str | Decimal]] = []
    secao: str | None = None

    for linha_bruta in texto.splitlines():
        linha_original = linha_bruta.strip()
        if not linha_original:
            continue

        linha_busca = _normalizar_para_busca(linha_original)
        if linha_busca.startswith("VANTAGENS"):
            secao = "vantagem"
            continue

        if linha_busca.startswith("DESCONTOS"):
            secao = "desconto"
            continue

        if linha_busca.startswith("TOTAL:") or "VALOR A RECEBER" in linha_busca:
            secao = None
            continue

        if secao is None:
            continue

        correspondencia = PADRAO_RUBRICA_VALOR_FINAL.search(linha_original)
        if not correspondencia:
            continue

        descricao = linha_original[: correspondencia.start("valor")].strip()
        descricao = re.sub(r"^\d+\s+\S+\s+", "", descricao).strip()
        descricao = re.sub(r"\s*[-–]\s*$", "", descricao).strip()
        descricao = re.sub(r"\s+\d+$", "", descricao).strip()
        descricao = re.sub(r"\s+de$", "", descricao, flags=re.IGNORECASE).strip()

        rubricas.append(
            {
                "tipo": secao,
                "descricao": descricao or linha_original,
                "valor": _converter_valor_monetario(correspondencia.group("valor")),
            }
        )

    return rubricas
