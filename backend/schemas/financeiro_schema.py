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


class EvolucaoSalarialSerieItemResponse(BaseModel):
    ano: int = Field(gt=0)
    valor_bruto_medio: float = Field(ge=0)
    quantidade_contracheques: int = Field(ge=0)


class EvolucaoSalarialResponse(BaseModel):
    batch_id: int = Field(gt=0)
    ano_inicial: int = Field(gt=0)
    ano_final: int = Field(gt=0)
    valor_inicial: float
    valor_final: float
    variacao_absoluta: float
    variacao_percentual: float
    series: list[EvolucaoSalarialSerieItemResponse] = Field(min_length=1)
