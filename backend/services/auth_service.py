from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.database.models import Usuario
from backend.repositories.usuario_repository import (
    atualizar_usuario,
    obter_usuario_por_login_ou_email,
    obter_usuario_por_sessao_token_hash,
)
from backend.schemas.auth_schema import UsuarioLoginRequest, UsuarioRedefinirSenhaRequest
from backend.services.security_service import gerar_hash_sha256, gerar_token_seguro


def _hash_token(valor: str) -> str:
    return gerar_hash_sha256(valor)


def autenticar_usuario(db: Session, dados: UsuarioLoginRequest) -> tuple[Usuario, str]:
    identificador = dados.login.strip()
    senha = dados.senha

    usuario = obter_usuario_por_login_ou_email(db, identificador)
    if usuario is None:
        raise ValueError("Login ou senha incorretos.")

    senha_hash = gerar_hash_sha256(senha)
    if usuario.senha_hash != senha_hash:
        raise ValueError("Login ou senha incorretos.")

    if not usuario.email_confirmado:
        raise ValueError("Confirme seu email antes de entrar.")

    token_sessao = gerar_token_seguro()
    usuario.sessao_token_hash = _hash_token(token_sessao)
    usuario.sessao_expira_em = datetime.now(timezone.utc) + timedelta(days=7)
    atualizar_usuario(db, usuario)

    return usuario, token_sessao


def obter_usuario_autenticado_por_token(
    db: Session,
    token: str,
) -> Usuario | None:
    return obter_usuario_por_sessao_token_hash(db, _hash_token(token))


def encerrar_sessao_usuario(db: Session, token: str) -> None:
    usuario = obter_usuario_autenticado_por_token(db, token)
    if usuario is None:
        return

    usuario.sessao_token_hash = None
    usuario.sessao_expira_em = None
    atualizar_usuario(db, usuario)


def redefinir_senha_usuario(
    db: Session,
    dados: UsuarioRedefinirSenhaRequest,
) -> None:
    identificador = dados.identificador.strip()
    usuario = obter_usuario_por_login_ou_email(db, identificador)
    if usuario is None:
        raise ValueError("Nao encontramos um usuario com esse login ou email.")

    usuario.senha_hash = gerar_hash_sha256(dados.nova_senha)
    usuario.sessao_token_hash = None
    usuario.sessao_expira_em = None
    atualizar_usuario(db, usuario)
