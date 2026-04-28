from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.auth_schema import UsuarioAuthResponse, UsuarioLoginRequest
from backend.schemas.usuario_schema import UsuarioResponse
from backend.services.usuario_service import (
    autenticar_usuario,
    encerrar_sessao_usuario,
    obter_usuario_autenticado_por_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _extrair_token_bearer(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nao autenticado.")

    esquema, _, token = authorization.partition(" ")
    if esquema.lower() != "bearer" or not token.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nao autenticado.")

    return token.strip()


@router.post("/login", response_model=UsuarioAuthResponse)
def login(
    dados: UsuarioLoginRequest,
    db: Session = Depends(get_db),
) -> UsuarioAuthResponse:
    try:
        usuario, token_sessao = autenticar_usuario(db, dados)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(erro)) from erro

    return UsuarioAuthResponse(
        access_token=token_sessao,
        usuario=UsuarioResponse.model_validate(usuario),
    )


@router.get("/me", response_model=UsuarioResponse)
def me(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    token = _extrair_token_bearer(authorization)
    usuario = obter_usuario_autenticado_por_token(db, token)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessao expirada.")

    return UsuarioResponse.model_validate(usuario)


@router.post("/logout")
def logout(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    token = _extrair_token_bearer(authorization)
    encerrar_sessao_usuario(db, token)
    return {"status": "ok"}

