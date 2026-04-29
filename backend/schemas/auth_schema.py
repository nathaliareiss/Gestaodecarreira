from __future__ import annotations

from pydantic import BaseModel, Field

from backend.schemas.usuario_schema import UsuarioResponse


class UsuarioLoginRequest(BaseModel):
    login: str = Field(min_length=1, max_length=80)
    senha: str = Field(min_length=1, max_length=128)


class UsuarioSolicitarRecuperacaoSenhaRequest(BaseModel):
    email: str = Field(min_length=1, max_length=254)


class UsuarioRedefinirSenhaRequest(BaseModel):
    token: str = Field(min_length=1)
    nova_senha: str = Field(min_length=6, max_length=128)


class UsuarioAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse
