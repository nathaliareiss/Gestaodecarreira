from __future__ import annotations

from pydantic import BaseModel, Field

from backend.schemas.usuario_schema import UsuarioResponse


class UsuarioLoginRequest(BaseModel):
    login: str = Field(min_length=1, max_length=80)
    senha: str = Field(min_length=1, max_length=128)


class UsuarioAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse
