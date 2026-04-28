from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from sqlalchemy.orm import Session

from backend.database.models import Usuario
from backend.repositories.usuario_repository import (
    criar_usuario,
    atualizar_usuario,
    obter_ultimo_usuario,
    listar_usuarios,
    obter_usuario_por_email,
    obter_usuario_por_login,
    obter_usuario_por_login_ou_email,
    obter_usuario_por_token,
    obter_usuario_por_sessao_token_hash,
    remover_usuario,
)
from backend.schemas.auth_schema import UsuarioLoginRequest
from backend.schemas.usuario_schema import UsuarioConfirmarRequest, UsuarioCreateRequest
from backend.services.email_service import enviar_email_confirmacao


def cadastrar_usuario(db: Session, cadastro: UsuarioCreateRequest) -> Usuario:
    nome = cadastro.nome.strip()
    apelido = cadastro.apelido.strip() or None
    email = cadastro.email.strip().lower()
    login = cadastro.login.strip()
    senha = cadastro.senha

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
        login=login,
        senha_hash=hashlib.sha256(senha.encode("utf-8")).hexdigest(),
        token_confirmacao_email=token_urlsafe(32),
        email_confirmado=False,
        criado_em=datetime.now(timezone.utc),
        confirmado_em=None,
    )
    usuario = criar_usuario(db, usuario)

    try:
        enviar_email_confirmacao(
            destinatario=usuario.email,
            nome=usuario.nome,
            token=usuario.token_confirmacao_email,
        )
        db.commit()
        db.refresh(usuario)
    except Exception as exc:
        db.rollback()
        raise RuntimeError(
            "Nao foi possivel enviar o email de confirmacao agora. Tente novamente."
        ) from exc

    return usuario


def _gerar_hash_token(valor: str) -> str:
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()


def autenticar_usuario(db: Session, dados: UsuarioLoginRequest) -> tuple[Usuario, str]:
    identificador = dados.login.strip()
    senha = dados.senha

    usuario = obter_usuario_por_login_ou_email(db, identificador)
    if usuario is None:
        raise ValueError("Login ou senha incorretos.")

    senha_hash = hashlib.sha256(senha.encode("utf-8")).hexdigest()
    if usuario.senha_hash != senha_hash:
        raise ValueError("Login ou senha incorretos.")

    if not usuario.email_confirmado:
        raise ValueError("Confirme seu email antes de entrar.")

    token_sessao = token_urlsafe(32)
    usuario.sessao_token_hash = _gerar_hash_token(token_sessao)
    usuario.sessao_expira_em = datetime.now(timezone.utc) + timedelta(days=7)
    atualizar_usuario(db, usuario)

    return usuario, token_sessao


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
    return atualizar_usuario(db, usuario)


def obter_usuario_autenticado_por_token(
    db: Session,
    token: str,
) -> Usuario | None:
    token_hash = _gerar_hash_token(token)
    return obter_usuario_por_sessao_token_hash(db, token_hash)


def encerrar_sessao_usuario(db: Session, token: str) -> None:
    usuario = obter_usuario_autenticado_por_token(db, token)
    if usuario is None:
        return

    usuario.sessao_token_hash = None
    usuario.sessao_expira_em = None
    atualizar_usuario(db, usuario)


def excluir_usuario_mais_recente(db: Session) -> Usuario | None:
    usuario = obter_ultimo_usuario(db)
    if usuario is None:
        return None

    remover_usuario(db, usuario)
    return usuario
