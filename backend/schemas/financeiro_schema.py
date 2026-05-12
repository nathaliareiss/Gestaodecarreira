from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ArquivoLoteFinanceiroPayload(BaseModel):
    arquivo_nome: str = Field(min_length=1)
    arquivo_temporario_path: str = Field(min_length=1)
    file_hash: str | None = None


class ArquivoFinanceiroJobPayload(BaseModel):
    batch_id: int = Field(gt=0)
    user_id: int | None = Field(default=None, gt=0)
    arquivo: ArquivoLoteFinanceiroPayload


class LoteFinanceiroJobPayload(BaseModel):
    batch_id: int = Field(gt=0)
    user_id: int | None = Field(default=None, gt=0)
    arquivos: list[ArquivoLoteFinanceiroPayload] = Field(min_length=1)


class LoteFinanceiroUploadResponse(BaseModel):
    batch_id: int = Field(gt=0)
    status: Literal["processing", "completed", "failed"]


class FinanceiroImportacaoTemporariaCriacaoResponse(BaseModel):
    token: str = Field(min_length=1)
    expires_at: datetime
    scope: str = Field(default="financeiro_importacao")


class FinanceiroImportacaoTemporariaValidacaoRequest(BaseModel):
    token: str = Field(min_length=1)


class FinanceiroImportacaoTemporariaValidacaoResponse(BaseModel):
    valid: bool
    scope: str = Field(default="financeiro_importacao")
    user_id: int = Field(gt=0)
    expires_at: datetime
    used: bool


class LoteFinanceiroStatusResponse(BaseModel):
    total: int = Field(ge=0)
    processed_count: int = Field(ge=0, default=0)
    duplicated_count: int = Field(ge=0, default=0)
    failed_count: int = Field(ge=0, default=0)
    status: Literal["pending", "processing", "completed", "failed"]
    last_error_message: str | None = None
    failure_messages: list[str] = Field(default_factory=list)
    processed: int = Field(ge=0, default=0)
    duplicated: int = Field(ge=0, default=0)
    failed: int = Field(ge=0, default=0)


class EvolucaoSalarialSerieItemResponse(BaseModel):
    ano: int = Field(gt=0)
    salario_base_referencia_anual: float = Field(ge=0)
    bruto_total_referencia_anual: float = Field(ge=0)
    liquido_referencia_anual: float = Field(ge=0)
    descontos_referencia_anual: float = Field(ge=0)
    vantagens_adicionais_referencia_anual: float = Field(ge=0)
    composicao_vantagens_referencia_anual: dict[str, float] = Field(default_factory=dict)
    composicao_descontos_referencia_anual: dict[str, float] = Field(default_factory=dict)
    quantidade_contracheques: int = Field(ge=0)
    variacao_percentual_salario_base_ano_a_ano: float | None = None
    crescimento_relevante: bool = True


class EvolucaoSalarialResponse(BaseModel):
    batch_id: int | None = None
    ano_inicial: int | None = None
    ano_final: int | None = None
    salario_base_inicial_referencia: float | None = None
    salario_base_final_referencia: float | None = None
    bruto_total_inicial_referencia: float | None = None
    bruto_total_final_referencia: float | None = None
    liquido_inicial_referencia: float | None = None
    liquido_final_referencia: float | None = None
    descontos_inicial_referencia: float | None = None
    descontos_final_referencia: float | None = None
    vantagens_adicionais_inicial_referencia: float | None = None
    vantagens_adicionais_final_referencia: float | None = None
    variacao_acumulada_salario_base_percentual: float | None = None
    anos_sem_crescimento_relevante: list[int] = Field(default_factory=list)
    series: list[EvolucaoSalarialSerieItemResponse] = Field(default_factory=list)


class ContrachequeResumoResponse(BaseModel):
    id: int = Field(gt=0)
    competencia: str = Field(min_length=1)
    ano: int = Field(gt=0)
    mes: int = Field(gt=0)
    salario_base: float
    bruto_total: float
    liquido: float
    descontos: float
