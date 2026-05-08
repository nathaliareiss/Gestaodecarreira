from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.logger import logger
from backend.cache.redis_cache import (
    CACHE_TTL_USUARIO_ULTIMO_SEGUNDOS,
    chave_usuario_ultimo,
    definir_json_cache,
    obter_json_cache,
)
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
from backend.services.email_service import enviar_email_confirmacao

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _obter_request_id(request: Request) -> str:
    return request.headers.get("x-request-id") or uuid4().hex


def _enviar_email_confirmacao_com_erro_isolado(destinatario: str, nome: str, token: str) -> None:
    try:
        enviar_email_confirmacao(destinatario=destinatario, nome=nome, token=token)
    except Exception:
        logger.exception(
            "Falha no envio do email de confirmacao em background",
            extra={"destinatario": destinatario},
        )


@router.post("", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    cadastro: UsuarioCreateRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    request_id = _obter_request_id(request)
    logger.info("Recebida solicitacao de cadastro", extra={"request_id": request_id})
    try:
        usuario = cadastrar_usuario(db, cadastro)
    except ValueError as erro:
        logger.warning("Cadastro recusado", extra={"request_id": request_id})
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(erro)) from erro
    except RuntimeError as erro:
        logger.exception("Falha ao cadastrar usuario", extra={"request_id": request_id})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nao foi possivel concluir o cadastro agora. Tente novamente mais tarde.",
        ) from erro

    background_tasks.add_task(
        _enviar_email_confirmacao_com_erro_isolado,
        destinatario=usuario.email,
        nome=usuario.nome,
        token=usuario.token_confirmacao_email,
    )
    logger.info("Cadastro concluido e email programado em background", extra={"request_id": request_id, "usuario_id": usuario.id})
    return UsuarioResponse.model_validate(usuario)


@router.get("", response_model=list[UsuarioResponse])
def listar_todos_os_usuarios(db: Session = Depends(get_db)) -> list[UsuarioResponse]:
    usuarios = consultar_usuarios(db)
    logger.debug("Listagem de usuarios consultada", extra={"total": len(usuarios)})
    return [UsuarioResponse.model_validate(usuario) for usuario in usuarios]


@router.get("/ultimo", response_model=UsuarioResponse)
def obter_ultimo_usuario(db: Session = Depends(get_db)) -> UsuarioResponse:
    cache = obter_json_cache(chave_usuario_ultimo())
    if cache is not None:
        logger.debug("Ultimo usuario carregado do cache")
        return UsuarioResponse.model_validate(cache)

    usuario = obter_usuario_mais_recente(db)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum usuario encontrado.",
        )

    logger.debug("Ultimo usuario consultado", extra={"usuario_id": usuario.id})
    resposta = UsuarioResponse.model_validate(usuario)
    definir_json_cache(chave_usuario_ultimo(), resposta.model_dump(mode="json"), CACHE_TTL_USUARIO_ULTIMO_SEGUNDOS)
    return resposta


@router.post("/confirmar", response_model=UsuarioResponse)
def confirmar_email(
    dados: UsuarioConfirmarRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    request_id = _obter_request_id(request)
    logger.info("Recebida confirmacao de email", extra={"request_id": request_id, "token_recebido": bool(dados.token)})
    try:
        usuario = confirmar_usuario(db, dados)
    except ValueError as erro:
        logger.warning("Confirmacao de email recusada", extra={"request_id": request_id, "motivo": str(erro)})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro

    logger.info("Email confirmado", extra={"request_id": request_id, "usuario_id": usuario.id})
    return UsuarioResponse.model_validate(usuario)


@router.delete("/ultimo", response_model=UsuarioResponse)
def remover_ultimo_usuario(db: Session = Depends(get_db)) -> UsuarioResponse:
    usuario = excluir_usuario_mais_recente(db)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum usuario encontrado.",
        )

    logger.info("Ultimo usuario removido", extra={"usuario_id": usuario.id})
    return UsuarioResponse.model_validate(usuario)
