from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.logger import logger

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.critical(
        "DATABASE_URL nao foi definido",
        extra={"arquivo": "backend/.env"},
    )
    raise RuntimeError(
        "DATABASE_URL nao foi definido. Configure backend/.env antes de iniciar o banco."
    )

def _garantir_sslmode_require(url: str) -> str:
    partes = urlparse(url)
    if not partes.hostname or not partes.hostname.endswith(".supabase.co"):
        return url

    query = dict(parse_qsl(partes.query, keep_blank_values=True))
    if "sslmode" in query:
        return url

    query["sslmode"] = "require"
    url_corrigida = urlunparse(partes._replace(query=urlencode(query)))
    logger.warning(
        "DATABASE_URL Supabase sem sslmode; aplicando sslmode=require automaticamente",
        extra={"host": partes.hostname, "porta": partes.port},
    )
    return url_corrigida


DATABASE_URL = _garantir_sslmode_require(DATABASE_URL)

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


@event.listens_for(engine, "connect")
def _configurar_contexto_rls_backend(dbapi_connection, connection_record) -> None:
    if _E_SQLITE:
        return

    cursor = dbapi_connection.cursor()
    cursor.execute("SET app.backend_access = 'on'")
    cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
