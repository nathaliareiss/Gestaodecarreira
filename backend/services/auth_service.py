from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.logger import logger
from backend.database.database import get_db
from backend.database.models import Usuario
from backend.repositories.usuario_repository import (
    atualizar_usuario,
    obter_usuario_por_email,
    obter_usuario_por_token,
    obter_usuario_por_redefinir_senha_token_hash,
    obter_usuario_por_sessao_token_hash,
    obter_usuario_por_login,
)
from backend.schemas.auth_schema import (
    UsuarioLoginRequest,
    UsuarioRedefinirSenhaRequest,
    UsuarioReenviarConfirmacaoRequest,
    UsuarioSolicitarRecuperacaoSenhaRequest,
)
from backend.schemas.usuario_schema import UsuarioConfirmarRequest
from backend.services.security_service import gerar_hash_sha256, gerar_token_seguro

AUTH_COOKIE_NAME = "gc_auth_token"
AUTH_COOKIE_MAX_AGE_SEGUNDOS = 60 * 60 * 24 * 7


def _hash_token(valor: str) -> str:
    return gerar_hash_sha256(valor)


def autenticar_usuario(db: Session, dados: UsuarioLoginRequest) -> tuple[Usuario, str]:
    identificador = dados.login.strip()
    senha = dados.senha
    logger.info("Processando autenticacao", extra={"identificador": identificador})

    if "@" in identificador:
        usuario = obter_usuario_por_email(db, identificador.lower())
        if usuario is None:
            raise ValueError("Nao encontramos um usuario cadastrado com este email.")
    else:
        usuario = obter_usuario_por_login(db, identificador)
        if usuario is None:
            raise ValueError("Nao encontramos um usuario cadastrado com este login.")

    senha_hash = gerar_hash_sha256(senha)
    if usuario.senha_hash != senha_hash:
        raise ValueError("Senha incorreta.")

    if not usuario.email_confirmado:
        raise ValueError("Confirme seu email antes de entrar.")

    token_sessao = gerar_token_seguro()
    registrar_sessao_usuario(db, usuario, token_sessao)
    logger.info(
        "Autenticacao concluida",
        extra={"usuario_id": usuario.id},
    )

    return usuario, token_sessao


def registrar_sessao_usuario(db: Session, usuario: Usuario, token_sessao: str) -> None:
    usuario.sessao_token_hash = _hash_token(token_sessao)
    usuario.sessao_expira_em = datetime.now(timezone.utc) + timedelta(days=7)
    db.add(usuario)
    db.commit()


def extrair_token_autenticacao(request: Request) -> str:
    authorization = request.headers.get("authorization")
    if authorization:
        esquema, _, token = authorization.partition(" ")
        if esquema.lower() == "bearer" and token.strip():
            return token.strip()

    token_cookie = request.cookies.get(AUTH_COOKIE_NAME)
    if token_cookie:
        return token_cookie.strip()

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nao autenticado.")


def extrair_token_autenticacao_opcional(request: Request) -> str | None:
    try:
        return extrair_token_autenticacao(request)
    except HTTPException:
        return None


def obter_usuario_autenticado_por_token(
    db: Session,
    token: str,
) -> Usuario | None:
    return obter_usuario_por_sessao_token_hash(db, _hash_token(token))


def obter_usuario_autenticado(
    request: Request,
    db: Session = Depends(get_db),
) -> Usuario:
    token = extrair_token_autenticacao(request)
    usuario = obter_usuario_autenticado_por_token(db, token)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessao expirada.")
    return usuario


def encerrar_sessao_usuario(db: Session, token: str) -> None:
    usuario = obter_usuario_autenticado_por_token(db, token)
    if usuario is None:
        logger.warning("Encerramento de sessao ignorado porque o token nao foi encontrado")
        return

    usuario.sessao_token_hash = None
    usuario.sessao_expira_em = None
    atualizar_usuario(db, usuario)
    logger.info(
        "Sessao encerrada",
        extra={"usuario_id": usuario.id},
    )


def confirmar_email_usuario(
    db: Session,
    dados: UsuarioConfirmarRequest,
) -> Usuario:
    usuario = obter_usuario_por_token(db, dados.token)
    if usuario is None:
        raise ValueError("Token de confirmacao invalido ou expirado.")

    usuario.email_confirmado = True
    usuario.confirmado_em = datetime.now(timezone.utc)
    usuario.token_confirmacao_email = gerar_token_seguro()
    atualizar_usuario(db, usuario)
    logger.info(
        "Confirmacao de email concluida",
        extra={"usuario_id": usuario.id},
    )
    return usuario


def solicitar_recuperacao_senha(
    db: Session,
    dados: UsuarioSolicitarRecuperacaoSenhaRequest,
) -> tuple[Usuario, str]:
    email = dados.email.strip().lower()
    logger.info("Processando recuperacao de senha", extra={"email": email})
    usuario = obter_usuario_por_email(db, email)
    if usuario is None:
        logger.warning(
            "Recuperacao solicitada para email nao cadastrado",
            extra={"email": email},
        )
        raise ValueError("Nao encontramos um usuario cadastrado com este email.")

    token = gerar_token_seguro()
    usuario.redefinir_senha_token_hash = _hash_token(token)
    usuario.redefinir_senha_expira_em = datetime.now(timezone.utc) + timedelta(minutes=30)
    db.add(usuario)
    db.flush()
    db.commit()
    logger.info(
        "Recuperacao de senha preparada",
        extra={"usuario_id": usuario.id, "email": email},
    )
    return usuario, token


def reenviar_confirmacao_email(
    db: Session,
    dados: UsuarioReenviarConfirmacaoRequest,
) -> tuple[Usuario, str]:
    identificador = dados.identificador.strip()
    logger.info("Processando reenvio de confirmacao")

    if "@" in identificador:
        usuario = obter_usuario_por_email(db, identificador.lower())
    else:
        usuario = obter_usuario_por_login(db, identificador)

    if usuario is None:
        raise ValueError("Nao encontramos um usuario cadastrado com esse login ou email.")

    if usuario.email_confirmado:
        raise ValueError("Este usuario ja esta com o email confirmado.")

    token = gerar_token_seguro()
    usuario.token_confirmacao_email = token
    db.add(usuario)
    db.commit()
    logger.info(
        "Confirmacao preparada para reenvio",
        extra={"usuario_id": usuario.id},
    )
    return usuario, token


def redefinir_senha_usuario(
    db: Session,
    dados: UsuarioRedefinirSenhaRequest,
) -> Usuario:
    usuario = obter_usuario_por_redefinir_senha_token_hash(db, _hash_token(dados.token))
    if usuario is None:
        raise ValueError("Token de redefinicao invalido ou expirado.")

    usuario.senha_hash = gerar_hash_sha256(dados.nova_senha)
    usuario.redefinir_senha_token_hash = None
    usuario.redefinir_senha_expira_em = None
    usuario.sessao_token_hash = None
    usuario.sessao_expira_em = None
    atualizar_usuario(db, usuario)
    logger.info(
        "Senha redefinida com sucesso",
        extra={"usuario_id": usuario.id},
    )
    return usuario
