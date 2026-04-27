from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CadastroCarreiraRequest(BaseModel):
    nome: str = Field(min_length=1)
    data_nascimento: date
    data_ingresso: date
    tem_tempo_clt_averbado: bool = False


class ResumoCarreiraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str
    data_nascimento: date
    data_ingresso: date
    tem_tempo_clt_averbado: bool
    data_25_anos_carreira: date
    idade_na_data_25_anos_carreira: int
    possui_idade_minima_na_data_25_anos_carreira: bool
    data_idade_minima_aposentadoria: date
    data_prevista_aposentadoria: date
    grau_aos_45_anos: str
    nivel_aos_45_anos: int
    grau_na_aposentadoria: str
    nivel_na_aposentadoria: int
