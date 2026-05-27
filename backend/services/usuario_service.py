from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
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
from backend.services.security_service import gerar_hash_sha256, gerar_token_seguro


def _mensagem_conflito_integridade(erro: IntegrityError) -> str | None:
    orig = getattr(erro, "orig", None)
    constraint_name = (
        getattr(getattr(orig, "diag", None), "constraint_name", None)
        or getattr(orig, "constraint_name", None)
        or ""
    ).lower()
    detalhes = " ".join(
        parte
        for parte in (
            str(erro),
            str(orig),
            str(getattr(orig, "diag", None)),
            constraint_name,
        )
        if parte
    ).lower()

    if any(
        trecho in detalhes
        for trecho in (
            "usuarios.email",
            "usuarios_email_key",
            "uq_usuarios_email",
            "unique constraint failed: usuarios.email",
        )
    ) or constraint_name in {"usuarios_email_key", "uq_usuarios_email"}:
        return "Ja existe um usuario cadastrado com este email."

    if any(
        trecho in detalhes
        for trecho in (
            "usuarios.login",
            "usuarios_login_key",
            "uq_usuarios_login",
            "unique constraint failed: usuarios.login",
        )
    ) or constraint_name in {"usuarios_login_key", "uq_usuarios_login"}:
        return "Ja existe um usuario cadastrado com este login."

    return None


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
        logger.warning(
            "Cadastro recusado porque o email ja existe",
            extra={"email": email, "login": login, "usuario_existente_id": email_existente.id},
        )
        raise ValueError("Ja existe um usuario cadastrado com este email.")

    login_existente = obter_usuario_por_login(db, login)
    if login_existente is not None:
        logger.warning(
            "Cadastro recusado porque o login ja existe",
            extra={"email": email, "login": login, "usuario_existente_id": login_existente.id},
        )
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
    try:
        usuario = criar_usuario(db, usuario)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        mensagem_conflito = _mensagem_conflito_integridade(exc)
        if mensagem_conflito:
            logger.warning(
                "Falha de cadastro por conflito de integridade",
                extra={"email": email, "login": login, "motivo": mensagem_conflito},
            )
            raise ValueError(mensagem_conflito) from exc

        logger.exception(
            "Falha ao concluir cadastro por integridade do banco",
            extra={"email": email, "login": login},
        )
        raise RuntimeError(
            "Nao foi possivel concluir o cadastro. Tente novamente."
        ) from exc
    except Exception as exc:
        db.rollback()
        logger.exception(
            "Falha ao concluir cadastro",
            extra={"email": email, "login": login},
        )
        raise RuntimeError(
            "Nao foi possivel concluir o cadastro. Tente novamente."
        ) from exc

    logger.info(
        "Cadastro concluido",
        extra={"usuario_id": usuario.id, "email": email, "login": login},
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
    usuario.token_confirmacao_email = gerar_token_seguro()
    logger.info(
        "Confirmacao de email concluida",
        extra={"usuario_id": usuario.id},
    )
    return atualizar_usuario(db, usuario)


def excluir_usuario_mais_recente(db: Session) -> Usuario | None:
    usuario = obter_ultimo_usuario(db)
    if usuario is None:
        return None

    remover_usuario(db, usuario)
    logger.info(
        "Usuario removido",
        extra={"usuario_id": usuario.id},
    )
    return usuario
