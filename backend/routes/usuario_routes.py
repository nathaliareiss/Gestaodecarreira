from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.logger import logger
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
    logger.info(
        "Recebida solicitacao de cadastro",
        extra={"email": cadastro.email.strip().lower(), "login": cadastro.login.strip()},
    )
    try:
        usuario = cadastrar_usuario(db, cadastro)
    except ValueError as erro:
        logger.warning(
            "Cadastro recusado",
            extra={"email": cadastro.email.strip().lower(), "login": cadastro.login.strip()},
        )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro)) from erro
    except RuntimeError as erro:
        logger.exception(
            "Falha ao cadastrar usuario",
            extra={"email": cadastro.email.strip().lower(), "login": cadastro.login.strip()},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nao foi possivel concluir o cadastro agora. Tente novamente mais tarde.",
        ) from erro

    logger.info(
        "Cadastro enviado com sucesso",
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )
    return UsuarioResponse.model_validate(usuario)


@router.get("", response_model=list[UsuarioResponse])
def listar_todos_os_usuarios(db: Session = Depends(get_db)) -> list[UsuarioResponse]:
    usuarios = consultar_usuarios(db)
    logger.debug("Listagem de usuarios consultada", extra={"total": len(usuarios)})
    return [UsuarioResponse.model_validate(usuario) for usuario in usuarios]


@router.get("/ultimo", response_model=UsuarioResponse)
def obter_ultimo_usuario(db: Session = Depends(get_db)) -> UsuarioResponse:
    usuario = obter_usuario_mais_recente(db)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum usuario encontrado.",
        )

    logger.debug("Ultimo usuario consultado", extra={"usuario_id": usuario.id, "email": usuario.email})
    return UsuarioResponse.model_validate(usuario)


@router.post("/confirmar", response_model=UsuarioResponse)
def confirmar_email(
    dados: UsuarioConfirmarRequest,
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    logger.info("Recebida confirmacao de email", extra={"token_recebido": bool(dados.token)})
    try:
        usuario = confirmar_usuario(db, dados)
    except ValueError as erro:
        logger.warning("Confirmacao de email recusada", extra={"motivo": str(erro)})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro

    logger.info(
        "Email confirmado",
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )
    return UsuarioResponse.model_validate(usuario)


@router.delete("/ultimo", response_model=UsuarioResponse)
def remover_ultimo_usuario(db: Session = Depends(get_db)) -> UsuarioResponse:
    usuario = excluir_usuario_mais_recente(db)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum usuario encontrado.",
        )

    logger.info(
        "Ultimo usuario removido",
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )
    return UsuarioResponse.model_validate(usuario)
