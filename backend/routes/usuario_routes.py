from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.usuario_schema import (
    UsuarioConfirmarRequest,
    UsuarioCreateRequest,
    UsuarioResponse,
)
from backend.services.usuario_service import (
    cadastrar_usuario,
    confirmar_usuario,
    consultar_usuarios,
    excluir_usuario_mais_recente,
    obter_usuario_mais_recente,
)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    cadastro: UsuarioCreateRequest,
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    try:
        usuario = cadastrar_usuario(db, cadastro)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro)) from erro

    return UsuarioResponse.model_validate(usuario)


@router.get("", response_model=list[UsuarioResponse])
def listar_todos_os_usuarios(db: Session = Depends(get_db)) -> list[UsuarioResponse]:
    usuarios = consultar_usuarios(db)
    return [UsuarioResponse.model_validate(usuario) for usuario in usuarios]


@router.get("/ultimo", response_model=UsuarioResponse)
def obter_ultimo_usuario(db: Session = Depends(get_db)) -> UsuarioResponse:
    usuario = obter_usuario_mais_recente(db)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum usuario encontrado.",
        )

    return UsuarioResponse.model_validate(usuario)


@router.post("/confirmar", response_model=UsuarioResponse)
def confirmar_email(
    dados: UsuarioConfirmarRequest,
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    try:
        usuario = confirmar_usuario(db, dados)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro

    return UsuarioResponse.model_validate(usuario)


@router.delete("/ultimo", response_model=UsuarioResponse)
def remover_ultimo_usuario(db: Session = Depends(get_db)) -> UsuarioResponse:
    usuario = excluir_usuario_mais_recente(db)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum usuario encontrado.",
        )

    return UsuarioResponse.model_validate(usuario)
