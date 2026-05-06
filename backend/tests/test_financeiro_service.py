from __future__ import annotations

from decimal import Decimal

import pytest

from backend.services.financeiro_service import (
    calcular_projecao_aposentadoria,
    calcular_projecao_salarial,
    calcular_taxa_media_anual,
)


def test_calcular_taxa_media_anual_cagr() -> None:
    taxa = calcular_taxa_media_anual(
        Decimal("5575"),
        Decimal("8200"),
        10,
    )

    assert taxa.quantize(Decimal("0.000001")) == Decimal("0.039338")


def test_calcular_projecao_aposentadoria_composta() -> None:
    taxa = calcular_taxa_media_anual(
        Decimal("5575"),
        Decimal("8200"),
        10,
    )

    projetado = calcular_projecao_aposentadoria(
        Decimal("8200"),
        taxa,
        12,
    )

    assert projetado == Decimal("13028.57")


def test_calcular_projecao_salarial_legacy_continua_funcionando() -> None:
    assert calcular_projecao_salarial(Decimal("5000"), Decimal("5")) == Decimal("5250")


@pytest.mark.parametrize(
    ("salario_inicial", "salario_final", "anos", "mensagem"),
    [
        (Decimal("0"), Decimal("8200"), 10, "salario inicial"),
        (Decimal("5575"), Decimal("8200"), 0, "anos"),
        (Decimal("-1"), Decimal("8200"), 10, "salario inicial"),
    ],
)
def test_calcular_taxa_media_anual_valida_entradas(
    salario_inicial: Decimal,
    salario_final: Decimal,
    anos: int,
    mensagem: str,
) -> None:
    with pytest.raises(ValueError, match=mensagem):
        calcular_taxa_media_anual(salario_inicial, salario_final, anos)


@pytest.mark.parametrize(
    ("salario_atual", "taxa_media_anual", "anos_restantes", "mensagem"),
    [
        (Decimal("-1"), Decimal("0.05"), 12, "salario atual"),
        (Decimal("8200"), Decimal("-1.1"), 12, "taxa media anual"),
        (Decimal("8200"), Decimal("0.05"), -1, "anos restantes"),
    ],
)
def test_calcular_projecao_aposentadoria_valida_entradas(
    salario_atual: Decimal,
    taxa_media_anual: Decimal,
    anos_restantes: int,
    mensagem: str,
) -> None:
    with pytest.raises(ValueError, match=mensagem):
        calcular_projecao_aposentadoria(salario_atual, taxa_media_anual, anos_restantes)
