from __future__ import annotations

import hashlib
from datetime import datetime, timezone
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
    obter_usuario_por_token,
    remover_usuario,
)
from backend.schemas.usuario_schema import UsuarioConfirmarRequest, UsuarioCreateRequest


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
    return criar_usuario(db, usuario)


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


def excluir_usuario_mais_recente(db: Session) -> Usuario | None:
    usuario = obter_ultimo_usuario(db)
    if usuario is None:
        return None

    remover_usuario(db, usuario)
    return usuario
