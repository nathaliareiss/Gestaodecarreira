from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class CadastroCarreiraSchema:
    nome: str
    data_nascimento: date
    data_ingresso: date
    tem_tempo_clt_averbado: bool = False


@dataclass(frozen=True, slots=True)
class ResumoCarreiraSchema:
    data_25_anos_carreira: date
    idade_na_data_25_anos_carreira: int
    possui_idade_minima_na_data_25_anos_carreira: bool
    data_idade_minima_aposentadoria: date
    data_prevista_aposentadoria: date
    grau_aos_45_anos: str
    nivel_aos_45_anos: int
    grau_na_aposentadoria: str
    nivel_na_aposentadoria: int
