from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.usuario_schema import UsuarioResponse


class UsuarioLoginRequest(BaseModel):
    login: str = Field(min_length=1, max_length=80)
    senha: str = Field(min_length=1, max_length=128)


class UsuarioAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class UsuarioSessaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario: UsuarioResponse
    expiracao: datetime | None

