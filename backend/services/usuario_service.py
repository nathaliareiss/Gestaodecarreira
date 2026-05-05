from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.logger import logger
from backend.database.models import Usuario
from backend.repositories.usuario_repository import (
    criar_usuario,
    atualizar_usuario,
    obter_ultimo_usuario,
    listar_usuarios,
    obter_usuario_por_email,
    obter_usuario_por_login,
    obter_usuario_por_token,
    remover_usuario,
)
from backend.schemas.usuario_schema import UsuarioConfirmarRequest, UsuarioCreateRequest
from backend.queue.email_dispatcher import agendar_email_confirmacao
from backend.services.security_service import gerar_hash_sha256, gerar_token_seguro


def cadastrar_usuario(db: Session, cadastro: UsuarioCreateRequest) -> Usuario:
    nome = cadastro.nome.strip()
    apelido = cadastro.apelido.strip() or None
    email = cadastro.email.strip().lower()
    login = cadastro.login.strip()
    senha = cadastro.senha
    logger.info(
        "Iniciando cadastro de usuario",
        extra={"email": email, "login": login},
    )

    email_existente = obter_usuario_por_email(db, email)
    if email_existente is not None:
        raise ValueError("Ja existe um usuario cadastrado com este email.")

    login_existente = obter_usuario_por_login(db, login)
    if login_existente is not None:
        raise ValueError("Ja existe um usuario cadastrado com este login.")

    usuario = Usuario(
        nome=nome,
        apelido=apelido,
        email=email,
        data_exercicio=cadastro.data_exercicio,
        login=login,
        senha_hash=gerar_hash_sha256(senha),
        token_confirmacao_email=gerar_token_seguro(),
        email_confirmado=False,
        criado_em=datetime.now(timezone.utc),
        confirmado_em=None,
    )
    usuario = criar_usuario(db, usuario)

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.exception("Falha ao concluir cadastro", extra={"email": email, "login": login})
        raise RuntimeError(
            "Nao foi possivel concluir o cadastro. Tente novamente."
        ) from exc

    try:
        agendar_email_confirmacao(
            destinatario=usuario.email,
            nome=usuario.nome,
            token=usuario.token_confirmacao_email,
        )
    except Exception:
        logger.exception(
            "Nao foi possivel agendar o email de confirmacao",
            extra={"email": email, "login": login},
        )

    logger.info(
        "Cadastro concluido",
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )

    return usuario


def consultar_usuarios(db: Session) -> list[Usuario]:
    return listar_usuarios(db)


def obter_usuario_mais_recente(db: Session) -> Usuario | None:
    return obter_ultimo_usuario(db)


def confirmar_usuario(db: Session, dados: UsuarioConfirmarRequest) -> Usuario:
    usuario = obter_usuario_por_token(db, dados.token)
    if usuario is None:
        raise ValueError("Token de confirmacao invalido.")

    usuario.email_confirmado = True
    usuario.confirmado_em = datetime.now(timezone.utc)
    logger.info(
        "Confirmacao de email concluida",
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )
    return atualizar_usuario(db, usuario)


def excluir_usuario_mais_recente(db: Session) -> Usuario | None:
    usuario = obter_ultimo_usuario(db)
    if usuario is None:
        return None

    remover_usuario(db, usuario)
    logger.info(
        "Usuario removido",
        extra={"usuario_id": usuario.id, "email": usuario.email},
    )
    return usuario
