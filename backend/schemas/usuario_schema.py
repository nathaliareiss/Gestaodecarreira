from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UsuarioCreateRequest(BaseModel):
    nome: str = Field(min_length=1)
    apelido: str = Field(default="", max_length=120)
    email: str = Field(min_length=5, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    login: str = Field(min_length=1, max_length=80)
    senha: str = Field(min_length=6, max_length=128)


class UsuarioConfirmarRequest(BaseModel):
    token: str = Field(min_length=1)


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    apelido: str | None
    email: str
    login: str
    senha_cadastrada: bool
    token_confirmacao_email: str
    email_confirmado: bool
    criado_em: datetime
    confirmado_em: datetime | None
