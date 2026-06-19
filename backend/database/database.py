from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session as OrmSession, declarative_base, sessionmaker

from backend.logger import logger

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    logger.critical(
        "DATABASE_URL nao foi definido",
        extra={"arquivo": "backend/.env"},
    )
    raise RuntimeError(
        "DATABASE_URL nao foi definido. Configure backend/.env antes de iniciar o banco."
)

_E_SQLITE = DATABASE_URL.startswith("sqlite")
_ENGINE_KWARGS = {"pool_pre_ping": True}
if _E_SQLITE:
    _ENGINE_KWARGS.update(
        {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    )

engine = create_engine(DATABASE_URL, **_ENGINE_KWARGS)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()

RLS_BACKEND_ACCESS_KEY = "rls_backend_access"
RLS_USER_ID_KEY = "rls_user_id"


def _aplicar_contexto_rls_na_conexao(
    connection,
    *,
    backend_access: bool,
    user_id: int | None,
) -> None:
    connection.execute(
        text("SELECT set_config('app.backend_access', :valor, true)"),
        {"valor": "on" if backend_access else "off"},
    )
    connection.execute(
        text("SELECT set_config('app.current_user_id', :valor, true)"),
        {"valor": "" if user_id is None else str(int(user_id))},
    )


@event.listens_for(OrmSession, "after_begin")
def _sincronizar_contexto_rls_da_sessao(session, transaction, connection) -> None:
    if _E_SQLITE:
        return

    _aplicar_contexto_rls_na_conexao(
        connection,
        backend_access=bool(session.info.get(RLS_BACKEND_ACCESS_KEY, False)),
        user_id=session.info.get(RLS_USER_ID_KEY),
    )


def configurar_contexto_rls(
    db: OrmSession,
    *,
    backend_access: bool = False,
    user_id: int | None = None,
) -> None:
    db.info[RLS_BACKEND_ACCESS_KEY] = backend_access
    db.info[RLS_USER_ID_KEY] = user_id

    if _E_SQLITE or not db.in_transaction():
        return

    _aplicar_contexto_rls_na_conexao(
        db.connection(),
        backend_access=backend_access,
        user_id=user_id,
    )


def ativar_acesso_backend(db: OrmSession) -> None:
    configurar_contexto_rls(db, backend_access=True, user_id=None)


def ativar_contexto_usuario(db: OrmSession, user_id: int) -> None:
    configurar_contexto_rls(db, backend_access=False, user_id=user_id)


def limpar_contexto_rls(db: OrmSession) -> None:
    configurar_contexto_rls(db, backend_access=False, user_id=None)


def get_db():
    db = SessionLocal()
    limpar_contexto_rls(db)
    try:
        yield db
    finally:
        db.close()
