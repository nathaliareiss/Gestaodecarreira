from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.database.models import Usuario


def listar_usuarios(db: Session) -> list[Usuario]:
    return list(db.scalars(select(Usuario).order_by(Usuario.id)))


def obter_usuario_por_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == email))


def obter_usuario_por_login(db: Session, login: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.login == login))


def obter_usuario_por_login_ou_email(db: Session, identificador: str) -> Usuario | None:
    return db.scalar(
        select(Usuario).where(
            or_(
                Usuario.login == identificador,
                Usuario.email == identificador,
            )
        )
    )


def obter_usuario_por_token(db: Session, token: str) -> Usuario | None:
    return db.scalar(
        select(Usuario).where(Usuario.token_confirmacao_email == token)
    )


def obter_usuario_por_sessao_token_hash(
    db: Session,
    token_hash: str,
) -> Usuario | None:
    return db.scalar(
        select(Usuario).where(
            Usuario.sessao_token_hash == token_hash,
            Usuario.sessao_expira_em.is_not(None),
            Usuario.sessao_expira_em > datetime.now(timezone.utc),
        )
    )


def obter_ultimo_usuario(db: Session) -> Usuario | None:
    return db.scalar(select(Usuario).order_by(Usuario.id.desc()))


def criar_usuario(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.flush()
    db.refresh(usuario)
    return usuario


def atualizar_usuario(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def remover_usuario(db: Session, usuario: Usuario) -> None:
    db.delete(usuario)
    db.commit()
