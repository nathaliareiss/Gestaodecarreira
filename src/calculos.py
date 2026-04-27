from datetime import date


def calcular_idade(data_nascimento: date, data_referencia: date | None = None) -> int:
    if data_referencia is None:
        data_referencia = date.today()

    idade = data_referencia.year - data_nascimento.year

    fez_aniversario = (
        data_referencia.month,
        data_referencia.day,
    ) >= (
        data_nascimento.month,
        data_nascimento.day,
    )

    if not fez_aniversario:
        idade -= 1

    return idade
