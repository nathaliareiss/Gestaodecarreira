from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HistoricoFuncionalUploadRequest(BaseModel):
    usuario_id: int | None = None
    arquivo_nome: str = Field(min_length=1)
    arquivo_base64: str = Field(min_length=1)
    data_nascimento: date
    anos_clt_averbados: int = Field(default=0, ge=0, le=10)


class HistoricoFuncionalEventoResponse(BaseModel):
    tipo: Literal["nomeacao", "progressao", "promocao", "substituicao"]
    descricao: str
    cargo: str
    simbolo: str
    nivel: str
    grau: str
    data_publicacao: date
    data_efetiva: date
    data_prevista: date | None
    status: Literal["cumprindo", "atrasado", "nao_aplicavel", "estagio_probatorio"]
    atraso_dias: int


class HistoricoFuncionalResumoGraficoResponse(BaseModel):
    tempo_trabalhado_dias: int
    tempo_restante_dias: int
    percentual_trabalhado: float
    percentual_restante: float
    eventos_totais: int
    eventos_por_status: dict[str, int]
    eventos_por_tipo: dict[str, int]


class HistoricoFuncionalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    historico_id: int
    usuario_id: int | None
    arquivo_nome: str
    nome: str
    masp: str
    cpf: str | None
    data_emissao: date | None
    data_nascimento: date
    data_posse: date
    data_exercicio: date
    cargo_atual: str
    simbolo_atual: str
    nivel_atual: str
    grau_atual: str
    tempo_clt_averbado_anos: int
    tempo_clt_creditado_anos: int
    data_aposentadoria_por_carreira: date
    data_aposentadoria_por_idade: date
    data_aposentadoria_prevista: date
    dias_trabalhados: int
    dias_totais_ate_aposentadoria: int
    percentual_trabalhado: float
    percentual_restante: float
    proxima_progressao_prevista: date
    proxima_promocao_prevista: date
    resumo_grafico: HistoricoFuncionalResumoGraficoResponse
    eventos: list[HistoricoFuncionalEventoResponse]
