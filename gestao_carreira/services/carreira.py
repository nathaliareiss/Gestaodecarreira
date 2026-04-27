from dataclasses import dataclass
from datetime import date

from gestao_carreira.domain.servidora import Servidora

from .datas import adicionar_anos, anos_completos_entre, calcular_idade


@dataclass(frozen=True, slots=True)
class ResumoFuncional:
    data_25_anos_carreira: date
    idade_na_data_25_anos_carreira: int
    possui_idade_minima_na_data_25_anos_carreira: bool
    data_idade_minima_aposentadoria: date
    data_prevista_aposentadoria: date
    grau_aos_45_anos: str
    nivel_aos_45_anos: int
    grau_na_aposentadoria: str
    nivel_na_aposentadoria: int


def calcular_grau(anos_de_carreira: int, grau_inicial: str = "A") -> str:
    incremento = anos_de_carreira // 2
    letra_inicial = grau_inicial.upper()
    return chr(ord(letra_inicial) + incremento)


def calcular_nivel(anos_de_carreira: int, nivel_inicial: int = 1) -> int:
    return nivel_inicial + (anos_de_carreira // 5)


def calcular_data_25_anos_carreira(data_ingresso: date) -> date:
    return adicionar_anos(data_ingresso, 25)


def calcular_data_idade_minima_aposentadoria(data_nascimento: date) -> date:
    return adicionar_anos(data_nascimento, 50)


def calcular_data_prevista_aposentadoria(
    data_nascimento: date,
    data_ingresso: date,
) -> date:
    data_carreira = calcular_data_25_anos_carreira(data_ingresso)
    data_idade_minima = calcular_data_idade_minima_aposentadoria(data_nascimento)
    return max(data_carreira, data_idade_minima)


def calcular_grau_e_nivel_em_data(
    data_ingresso: date,
    data_referencia: date,
) -> tuple[str, int]:
    anos_de_carreira = anos_completos_entre(data_ingresso, data_referencia)
    grau = calcular_grau(anos_de_carreira)
    nivel = calcular_nivel(anos_de_carreira)
    return grau, nivel


def montar_resumo_funcional(servidora: Servidora) -> ResumoFuncional:
    data_25_anos_carreira = calcular_data_25_anos_carreira(servidora.data_ingresso)
    idade_na_data_25_anos_carreira = calcular_idade(
        servidora.data_nascimento,
        data_25_anos_carreira,
    )
    possui_idade_minima = idade_na_data_25_anos_carreira >= 50
    data_idade_minima = calcular_data_idade_minima_aposentadoria(
        servidora.data_nascimento
    )
    data_prevista_aposentadoria = calcular_data_prevista_aposentadoria(
        servidora.data_nascimento,
        servidora.data_ingresso,
    )
    data_com_45_anos = adicionar_anos(servidora.data_nascimento, 45)
    grau_aos_45_anos, nivel_aos_45_anos = calcular_grau_e_nivel_em_data(
        servidora.data_ingresso,
        data_com_45_anos,
    )
    grau_na_aposentadoria, nivel_na_aposentadoria = calcular_grau_e_nivel_em_data(
        servidora.data_ingresso,
        data_prevista_aposentadoria,
    )

    return ResumoFuncional(
        data_25_anos_carreira=data_25_anos_carreira,
        idade_na_data_25_anos_carreira=idade_na_data_25_anos_carreira,
        possui_idade_minima_na_data_25_anos_carreira=possui_idade_minima,
        data_idade_minima_aposentadoria=data_idade_minima,
        data_prevista_aposentadoria=data_prevista_aposentadoria,
        grau_aos_45_anos=grau_aos_45_anos,
        nivel_aos_45_anos=nivel_aos_45_anos,
        grau_na_aposentadoria=grau_na_aposentadoria,
        nivel_na_aposentadoria=nivel_na_aposentadoria,
    )

