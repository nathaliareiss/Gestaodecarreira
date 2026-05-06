from __future__ import annotations

from backend.services.financeiro_service import calcular_projecao_salarial


def test_calculo_financeiro_com_salario_e_crescimento() -> None:
    assert calcular_projecao_salarial(5000, 5) == 5250.0
