from __future__ import annotations

from decimal import Decimal

from backend.services.contracheque_parser import parse_contracheque


def test_parse_contracheque_lido_do_layout_real(monkeypatch) -> None:
    from backend.services import contracheque_parser as parser

    texto_real = """
    DEMONSTRATIVO DE PAGAMENTO - JANEIRO/2025
    Vantagens
    1 Normal Adicional Desempenho 10 - 591,04
    1 Normal Adic Not Divisor -dj 28 - 182,04
    1 Normal Vencimento Basico 0 - 5.910,41
    Total: R$ 8.816,54
    Descontos
    1 Normal Contrib.prev.art. 28 0 - 842,08
    1 Normal B.pan - Emprest. i 0 4 de 120 360,19
    1 Normal Imp. Renda Ret.fonte 0 - 710,39
    Total: R$ 1.912,66
    Valor a receber R$ 6.903,88
    """

    monkeypatch.setattr(parser, "_extrair_texto_pdf", lambda _pdf_path: texto_real)

    dados = parse_contracheque("qualquer.pdf")

    assert dados == {
        "competencia": "Janeiro/2025",
        "ano": 2025,
        "mes": 1,
        "bruto": Decimal("8816.54"),
        "descontos": Decimal("1912.66"),
        "liquido": Decimal("6903.88"),
        "vencimento_basico": Decimal("5910.41"),
        "adicional_desempenho": Decimal("591.04"),
        "adicional_noturno": Decimal("182.04"),
        "irrf": Decimal("710.39"),
        "previdencia": Decimal("842.08"),
    }


def test_parse_contracheque_preenche_campos_ausentes_com_zero(monkeypatch) -> None:
    from backend.services import contracheque_parser as parser

    texto_simulado = """
    COMPETENCIA: Fevereiro/2023
    VENCIMENTO BASICO 4.000,00
    TOTAL DE VANTAGENS 4.250,00
    LIQUIDO 4.000,00
    """

    monkeypatch.setattr(parser, "_extrair_texto_pdf", lambda _pdf_path: texto_simulado)

    dados = parse_contracheque("qualquer.pdf")

    assert dados["competencia"] == "Fevereiro/2023"
    assert dados["ano"] == 2023
    assert dados["mes"] == 2
    assert dados["bruto"] == Decimal("4250.00")
    assert dados["descontos"] == Decimal("0.00")
    assert dados["liquido"] == Decimal("4000.00")
    assert dados["vencimento_basico"] == Decimal("4000.00")
    assert dados["adicional_desempenho"] == Decimal("0.00")
    assert dados["adicional_noturno"] == Decimal("0.00")
    assert dados["irrf"] == Decimal("0.00")
    assert dados["previdencia"] == Decimal("0.00")
