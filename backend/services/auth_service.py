from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.logger import logger
from backend.database.models import Usuario
from backend.repositories.usuario_repository import (
    atualizar_usuario,
    obter_usuario_por_email,
    obter_usuario_por_redefinir_senha_token_hash,
    obter_usuario_por_sessao_token_hash,
    obter_usuario_por_login,
)
from backend.schemas.auth_schema import (
    UsuarioLoginRequest,
    UsuarioRedefinirSenhaRequest,
    UsuarioSolicitarRecuperacaoSenhaRequest,
)
from backend.queue.email_dispatcher import agendar_email_recuperacao_senha
from backend.services.security_service import gerar_hash_sha256, gerar_token_seguro


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
    usuario.sessao_token_hash = _hash_token(token_sessao)
    usuario.sessao_expira_em = datetime.now(timezone.utc) + timedelta(days=7)
    db.add(usuario)
    db.commit()
    logger.info(
        "Autenticacao concluida",
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )

    return usuario, token_sessao


def obter_usuario_autenticado_por_token(
    db: Session,
    token: str,
) -> Usuario | None:
    return obter_usuario_por_sessao_token_hash(db, _hash_token(token))


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
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )


def solicitar_recuperacao_senha(
    db: Session,
    dados: UsuarioSolicitarRecuperacaoSenhaRequest,
) -> bool:
    email = dados.email.strip().lower()
    logger.info("Processando recuperacao de senha", extra={"email": email})
    usuario = obter_usuario_por_email(db, email)
    if usuario is None:
        logger.warning("Recuperacao solicitada para email nao cadastrado", extra={"email": email})
        return False

    token = gerar_token_seguro()
    usuario.redefinir_senha_token_hash = _hash_token(token)
    usuario.redefinir_senha_expira_em = datetime.now(timezone.utc) + timedelta(minutes=30)
    db.add(usuario)
    db.flush()

    try:
        agendar_email_recuperacao_senha(
            destinatario=usuario.email,
            nome=usuario.nome,
            token=token,
        )
        db.commit()
        logger.info(
            "Email de recuperacao enviado",
            extra={"usuario_id": usuario.id, "email": usuario.email},
        )
    except Exception:
        db.rollback()
        raise

    return True


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
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )
    return usuario
