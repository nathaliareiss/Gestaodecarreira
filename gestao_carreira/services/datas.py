from datetime import date


def adicionar_anos(data_base: date, anos: int) -> date:
    try:
        return data_base.replace(year=data_base.year + anos)
    except ValueError:
        return data_base.replace(year=data_base.year + anos, day=28)


def calcular_idade(data_nascimento: date, data_referencia: date | None = None) -> int:
    if data_referencia is None:
        data_referencia = date.today()

    idade = data_referencia.year - data_nascimento.year

    if (data_referencia.month, data_referencia.day) < (
        data_nascimento.month,
        data_nascimento.day,
    ):
        idade -= 1

    return idade


def anos_completos_entre(data_inicio: date, data_fim: date) -> int:
    anos = data_fim.year - data_inicio.year

    if (data_fim.month, data_fim.day) < (data_inicio.month, data_inicio.day):
        anos -= 1

    return anos

