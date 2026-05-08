from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ArquivoLoteFinanceiroPayload(BaseModel):
    arquivo_nome: str = Field(min_length=1)
    arquivo_temporario_path: str = Field(min_length=1)


class LoteFinanceiroJobPayload(BaseModel):
    batch_id: int = Field(gt=0)
    user_id: int | None = Field(default=None, gt=0)
    arquivos: list[ArquivoLoteFinanceiroPayload] = Field(min_length=1)


class LoteFinanceiroUploadResponse(BaseModel):
    batch_id: int = Field(gt=0)
    status: Literal["processing", "completed", "failed"]


class LoteFinanceiroStatusResponse(BaseModel):
    total: int = Field(ge=0)
    processed: int = Field(ge=0)
    failed: int = Field(ge=0)
    status: Literal["pending", "processing", "completed", "failed"]
    last_error_message: str | None = None
    failure_messages: list[str] = Field(default_factory=list)


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
    batch_id: int = Field(gt=0)
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
