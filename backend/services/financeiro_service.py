from __future__ import annotations


def calcular_projecao_salarial(salario_atual: float, crescimento_percentual: float) -> float:
    if salario_atual < 0:
        raise ValueError("O salario atual nao pode ser negativo.")

    if crescimento_percentual < -100:
        raise ValueError("O crescimento percentual nao pode ser menor que -100.")

    salario_projetado = salario_atual * (1 + crescimento_percentual / 100)
    return round(salario_projetado, 2)
