from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, localcontext

ZERO = Decimal("0")
UM = Decimal("1")
CENTO = Decimal("100")
CENTAVOS = Decimal("0.01")


def _validar_decimal_nao_negativo(valor: Decimal, nome: str) -> None:
    if valor < ZERO:
        raise ValueError(f"{nome} nao pode ser negativo.")


def calcular_taxa_media_anual(
    salario_inicial: Decimal,
    salario_final: Decimal,
    anos: int,
) -> Decimal:
    """Calcula a taxa media anual composta entre dois salarios."""

    _validar_decimal_nao_negativo(salario_inicial, "O salario inicial")
    _validar_decimal_nao_negativo(salario_final, "O salario final")

    if salario_inicial == ZERO:
        raise ValueError("O salario inicial deve ser maior que zero.")

    if salario_final == ZERO:
        return Decimal("-1")

    if anos <= 0:
        raise ValueError("A quantidade de anos deve ser maior que zero.")

    # CAGR = ((salario_final / salario_inicial) ** (1 / anos)) - 1
    # A potencia usa Decimal para manter a base monetaria precisa.
    with localcontext() as contexto:
        contexto.prec = 28
        razao = salario_final / salario_inicial
        expoente = UM / Decimal(anos)
        taxa = razao ** expoente

    return taxa - UM


def calcular_projecao_aposentadoria(
    salario_atual: Decimal,
    taxa_media_anual: Decimal,
    anos_restantes: int,
) -> Decimal:
    """Projeta o salario futuro usando crescimento composto anual."""

    _validar_decimal_nao_negativo(salario_atual, "O salario atual")

    if taxa_media_anual < Decimal("-1"):
        raise ValueError("A taxa media anual nao pode ser menor que -100%.")

    if anos_restantes < 0:
        raise ValueError("A quantidade de anos restantes nao pode ser negativa.")

    # salario_futuro = salario_atual * (1 + taxa_anual) ** anos
    with localcontext() as contexto:
        contexto.prec = 28
        fator = (UM + taxa_media_anual) ** Decimal(anos_restantes)
        projecao = salario_atual * fator

    return projecao.quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def calcular_projecao_salarial(
    salario_atual: Decimal,
    crescimento_percentual: Decimal,
) -> Decimal:
    """Compatibilidade com a regra antiga de um unico periodo."""

    _validar_decimal_nao_negativo(salario_atual, "O salario atual")

    if crescimento_percentual < Decimal("-100"):
        raise ValueError("O crescimento percentual nao pode ser menor que -100.")

    fator = UM + (crescimento_percentual / CENTO)
    return salario_atual * fator
