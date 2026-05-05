from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.logger import logger
from backend.schemas.auth_schema import (
    UsuarioAuthResponse,
    UsuarioLoginRequest,
    UsuarioRedefinirSenhaRequest,
    UsuarioReenviarConfirmacaoRequest,
    UsuarioSolicitarRecuperacaoSenhaRequest,
)
from backend.schemas.usuario_schema import UsuarioResponse
from backend.services.auth_service import (
    autenticar_usuario,
    encerrar_sessao_usuario,
    obter_usuario_autenticado_por_token,
    redefinir_senha_usuario,
    reenviar_confirmacao_email,
    solicitar_recuperacao_senha,
)
from backend.services.email_service import (
    enviar_email_confirmacao,
    enviar_email_recuperacao_senha,
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
    identificador = dados.login.strip()
    logger.info("Recebida solicitacao de login", extra={"identificador": identificador})
    try:
        usuario, token_sessao = autenticar_usuario(db, dados)
    except ValueError as erro:
        logger.warning(
            "Login recusado",
            extra={"identificador": identificador, "motivo": str(erro)},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(erro)) from erro

    logger.info(
        "Login concluido",
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )
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
        logger.warning("Sessao expirada ou invalida", extra={"rota": "/auth/me"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessao expirada.")

    logger.debug(
        "Usuario autenticado consultado",
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )
    return UsuarioResponse.model_validate(usuario)


@router.post("/logout")
def logout(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    token = _extrair_token_bearer(authorization)
    usuario = obter_usuario_autenticado_por_token(db, token)
    encerrar_sessao_usuario(db, token)
    logger.info(
        "Sessao encerrada",
        extra={
            "usuario_id": usuario.id if usuario else None,
            "email": usuario.email if usuario else None,
        },
    )
    return {"status": "ok"}


@router.post("/solicitar-recuperacao-senha")
def solicitar_recuperacao(
    dados: UsuarioSolicitarRecuperacaoSenhaRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    email = dados.email.strip().lower()
    logger.info("Recebida solicitacao de recuperacao de senha", extra={"email": email})
    try:
        usuario, token = solicitar_recuperacao_senha(db, dados)
    except ValueError:
        logger.info(
            "Solicitacao de recuperacao ignorada porque o email nao esta cadastrado",
            extra={"email": email},
        )
    except RuntimeError as erro:
        logger.exception(
            "Falha ao solicitar recuperacao de senha",
            extra={"email": email},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nao foi possivel enviar o email de recuperacao agora. Tente novamente mais tarde.",
        ) from erro
    else:
        background_tasks.add_task(
            enviar_email_recuperacao_senha,
            destinatario=usuario.email,
            nome=usuario.nome,
            token=token,
        )

    logger.info("Solicitacao de recuperacao processada", extra={"email": email})
    return {
        "status": "ok",
        "message": "Se o email estiver cadastrado, voce vai receber o link de redefinicao.",
    }


@router.post("/reenviar-confirmacao-email")
def reenviar_confirmacao(
    dados: UsuarioReenviarConfirmacaoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    identificador = dados.identificador.strip()
    logger.info(
        "Recebida solicitacao de reenvio de confirmacao",
        extra={"identificador": identificador},
    )
    try:
        usuario, token = reenviar_confirmacao_email(db, dados)
    except ValueError as erro:
        logger.warning(
            "Reenvio de confirmacao recusado",
            extra={"identificador": identificador, "motivo": str(erro)},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro

    background_tasks.add_task(
        enviar_email_confirmacao,
        destinatario=usuario.email,
        nome=usuario.nome,
        token=token,
    )
    logger.info(
        "Email de confirmacao agendado para reenvio",
        extra={"usuario_id": usuario.id, "email": usuario.email},
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
            extra={"motivo": str(erro)},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro)) from erro

    logger.info(
        "Senha redefinida com sucesso",
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )
    return {"status": "ok", "message": "Senha atualizada com sucesso."}
