from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from backend.services.contracheque_parser import parse_contracheque


FIXTURE_PDF = Path(__file__).parent / "fixtures" / "contracheque_exemplo.pdf"


def test_parse_contracheque_lido_do_pdf_real() -> None:
    dados = parse_contracheque(str(FIXTURE_PDF))

    assert dados == {
        "competencia": "Janeiro/2022",
        "ano": 2022,
        "mes": 1,
        "bruto": Decimal("5375.07"),
        "descontos": Decimal("550.00"),
        "liquido": Decimal("4825.07"),
        "vencimento_basico": Decimal("5000.00"),
        "adicional_desempenho": Decimal("300.00"),
        "adicional_noturno": Decimal("75.07"),
        "irrf": Decimal("200.00"),
        "previdencia": Decimal("350.00"),
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
