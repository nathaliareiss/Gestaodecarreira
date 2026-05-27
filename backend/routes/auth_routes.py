from __future__ import annotations

from uuid import uuid4
from urllib.parse import urlparse

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from backend.config import FRONTEND_BASE_URL
from backend.database.database import get_db
from backend.logger import logger
from backend.schemas.auth_schema import (
    UsuarioAuthResponse,
    UsuarioLoginRequest,
    UsuarioRedefinirSenhaRequest,
    UsuarioReenviarConfirmacaoRequest,
    UsuarioSolicitarRecuperacaoSenhaRequest,
)
from backend.schemas.usuario_schema import UsuarioConfirmarRequest, UsuarioResponse
from backend.services.auth_service import (
    AUTH_COOKIE_MAX_AGE_SEGUNDOS,
    AUTH_COOKIE_NAME,
    autenticar_usuario,
    confirmar_email_usuario,
    encerrar_sessao_usuario,
    extrair_token_autenticacao_opcional,
    obter_usuario_autenticado,
    obter_usuario_autenticado_por_token,
    redefinir_senha_usuario,
    reenviar_confirmacao_email,
    registrar_sessao_usuario,
    solicitar_recuperacao_senha,
)
from backend.services.security_service import gerar_token_seguro
from backend.services.email_service import (
    enviar_email_confirmacao,
    enviar_email_recuperacao_senha,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _enviar_email_confirmacao_com_erro_isolado(destinatario: str, nome: str, token: str) -> None:
    try:
        enviar_email_confirmacao(destinatario=destinatario, nome=nome, token=token)
    except Exception as erro:
        logger.exception(
            "Falha no reenvio do email de confirmacao em background",
            extra={"destinatario": destinatario, "erro_tipo": type(erro).__name__},
        )


def _enviar_email_recuperacao_com_erro_isolado(destinatario: str, nome: str, token: str) -> None:
    try:
        enviar_email_recuperacao_senha(destinatario=destinatario, nome=nome, token=token)
    except Exception as erro:
        logger.exception(
            "Falha no envio do email de recuperacao em background",
            extra={"destinatario": destinatario, "erro_tipo": type(erro).__name__},
        )


def _obter_request_id(request: Request) -> str:
    return request.headers.get("x-request-id") or uuid4().hex


def _cookie_deve_ser_seguro(request: Request) -> bool:
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    return proto.split(",")[0].strip().lower() == "https"


def _cookie_same_site(request: Request) -> str:
    """
    Keep local same-site auth working, but allow production cross-site fetches
    to send the session cookie when the frontend and backend are on different hosts.
    """

    frontend_host = urlparse(FRONTEND_BASE_URL).hostname if FRONTEND_BASE_URL else None
    request_host = request.url.hostname

    if frontend_host and request_host:
        if frontend_host == request_host:
            return "lax"

        if {frontend_host, request_host} <= {"localhost", "127.0.0.1"}:
            return "lax"

    return "none" if _cookie_deve_ser_seguro(request) else "lax"


def _aplicar_cookie_autenticacao(
    response: Response,
    request: Request,
    token_sessao: str,
) -> None:
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token_sessao,
        max_age=AUTH_COOKIE_MAX_AGE_SEGUNDOS,
        path="/",
        httponly=True,
        secure=_cookie_deve_ser_seguro(request),
        samesite=_cookie_same_site(request),
    )


@router.post("/login", response_model=UsuarioAuthResponse)
def login(
    dados: UsuarioLoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
) -> UsuarioAuthResponse:
    request_id = _obter_request_id(request)
    logger.info("Recebida solicitacao de login", extra={"request_id": request_id})
    try:
        usuario, token_sessao = autenticar_usuario(db, dados)
    except ValueError as erro:
        logger.warning(
            "Login recusado",
            extra={"request_id": request_id, "motivo": str(erro)},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(erro)) from erro

    _aplicar_cookie_autenticacao(response, request, token_sessao)
    logger.info(
        "Login concluido",
        extra={"request_id": request_id, "usuario_id": usuario.id},
    )
    return UsuarioAuthResponse(
        usuario=UsuarioResponse.model_validate(usuario),
    )


@router.get("/me", response_model=UsuarioResponse)
def me(
    request: Request,
    db: Session = Depends(get_db),
) -> UsuarioResponse:
    usuario = obter_usuario_autenticado(request, db)
    logger.debug(
        "Usuario autenticado consultado",
        extra={"usuario_id": usuario.id},
    )
    return UsuarioResponse.model_validate(usuario)


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    token = extrair_token_autenticacao_opcional(request)
    usuario = obter_usuario_autenticado_por_token(db, token) if token else None
    if token:
        encerrar_sessao_usuario(db, token)

    response.delete_cookie(key=AUTH_COOKIE_NAME, path="/")
    logger.info(
        "Sessao encerrada",
        extra={
            "usuario_id": usuario.id if usuario else None,
        },
    )
    return {"status": "ok"}


@router.post("/solicitar-recuperacao-senha")
def solicitar_recuperacao(
    dados: UsuarioSolicitarRecuperacaoSenhaRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    logger.info(
        "Recebida solicitacao de recuperacao de senha",
        extra={"email": dados.email.strip().lower()},
    )
    try:
        usuario, token = solicitar_recuperacao_senha(db, dados)
    except ValueError:
        logger.info(
            "Solicitacao de recuperacao ignorada porque o email nao esta cadastrado",
            extra={"email": dados.email.strip().lower()},
        )
    except RuntimeError as erro:
        logger.exception(
            "Falha ao solicitar recuperacao de senha",
            extra={"email": dados.email.strip().lower(), "erro_tipo": type(erro).__name__},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nao foi possivel enviar o email de recuperacao agora. Tente novamente mais tarde.",
        ) from erro
    else:
        background_tasks.add_task(
            _enviar_email_recuperacao_com_erro_isolado,
            destinatario=usuario.email,
            nome=usuario.nome,
            token=token,
        )

    logger.info("Solicitacao de recuperacao processada")
    return {
        "status": "ok",
        "message": "Se o email estiver cadastrado, voce vai receber o link de redefinicao.",
    }


@router.post("/confirmar-email", response_model=UsuarioAuthResponse)
def confirmar_email(
    dados: UsuarioConfirmarRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db),
) -> UsuarioAuthResponse:
    request_id = _obter_request_id(request)
    logger.info(
        "Recebida solicitacao de confirmacao de email",
        extra={"request_id": request_id, "token_recebido": bool(dados.token)},
    )
    try:
        usuario = confirmar_email_usuario(db, dados)
    except ValueError as erro:
        logger.warning(
            "Confirmacao de email recusada",
            extra={"request_id": request_id, "motivo": str(erro), "token_recebido": bool(dados.token)},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Este link expirou ou j\u00e1 foi utilizado.",
        ) from erro

    token_sessao = gerar_token_seguro()
    registrar_sessao_usuario(db, usuario, token_sessao)
    _aplicar_cookie_autenticacao(response, request, token_sessao)
    logger.info(
        "Email confirmado e sessao criada",
        extra={"request_id": request_id, "usuario_id": usuario.id},
    )
    return UsuarioAuthResponse(usuario=UsuarioResponse.model_validate(usuario))


@router.post("/reenviar-confirmacao-email")
def reenviar_confirmacao(
    dados: UsuarioReenviarConfirmacaoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    logger.info("Recebida solicitacao de reenvio de confirmacao")
    try:
        usuario, token = reenviar_confirmacao_email(db, dados)
    except ValueError as erro:
        logger.warning(
            "Reenvio de confirmacao recusado",
            extra={"motivo": str(erro), "identificador": dados.identificador.strip()},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro

    background_tasks.add_task(
        _enviar_email_confirmacao_com_erro_isolado,
        destinatario=usuario.email,
        nome=usuario.nome,
        token=token,
    )
    logger.info(
        "Email de confirmacao agendado para reenvio",
        extra={"usuario_id": usuario.id},
    )
    return {
        "status": "ok",
        "message": "Se o cadastro ainda estiver pendente, um novo email de confirmacao foi enviado.",
    }


@router.post("/redefinir-senha")
def redefinir_senha(
    dados: UsuarioRedefinirSenhaRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    logger.info("Recebida solicitacao de redefinicao de senha", extra={"token_recebido": bool(dados.token)})
    try:
        usuario = redefinir_senha_usuario(db, dados)
    except ValueError as erro:
        logger.warning(
            "Redefinicao de senha recusada",
            extra={"motivo": str(erro), "token_recebido": bool(dados.token)},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro

    logger.info(
        "Senha redefinida com sucesso",
        extra={"usuario_id": usuario.id},
    )
    return {"status": "ok", "message": "Senha atualizada com sucesso."}
