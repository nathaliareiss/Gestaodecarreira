from decimal import Decimal


def calcular_projecao_salarial(
    salario_atual: Decimal,
    crescimento_percentual: Decimal,
) -> Decimal:

    if salario_atual < 0:
        raise ValueError(
            "O salário atual não pode ser negativo."
        )

    if crescimento_percentual < -100:
        raise ValueError(
            "O crescimento percentual não pode ser menor que -100."
        )

    fator = Decimal("1") + (
        crescimento_percentual / Decimal("100")
    )

    return salario_atual * fator