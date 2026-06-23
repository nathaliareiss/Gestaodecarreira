from __future__ import annotations

from functools import lru_cache
from typing import Any

from backend.config import REDIS_URL
from backend.logger import logger

try:
    from redis import Redis
    from rq import Queue
    from rq.job import Job
except ImportError:  # pragma: no cover - fallback quando as dependencias ainda nao foram instaladas
    Redis = None
    Job = None
    Queue = None


def _fila_disponivel() -> bool:
    return Redis is not None and Queue is not None and bool(REDIS_URL)


@lru_cache(maxsize=1)
def obter_conexao_redis() -> Redis | None:
    if not _fila_disponivel():
        logger.warning(
            "Fila Redis indisponivel",
            extra={"redis_configurado": bool(REDIS_URL), "dependencias_instaladas": Redis is not None},
        )
        return None

    assert Redis is not None
    try:
        conexao = Redis.from_url(REDIS_URL, decode_responses=False)
        conexao.ping()
        return conexao
    except Exception as erro:
        logger.warning(
            "Nao foi possivel conectar ao Redis",
            extra={"redis_url_configurado": bool(REDIS_URL), "erro": str(erro)},
        )
        return None


@lru_cache(maxsize=1)
def obter_fila_historicos() -> Queue | None:
    if Queue is None:
        return None

    conexao = obter_conexao_redis()
    if conexao is None:
        return None

    return Queue(
        "historicos",
        connection=conexao,
        default_timeout=900,
        result_ttl=86400,
    )


@lru_cache(maxsize=1)
def obter_fila_financeiro() -> Queue | None:
    if Queue is None:
        return None

    conexao = obter_conexao_redis()
    if conexao is None:
        return None

    return Queue(
        "financeiro",
        connection=conexao,
        default_timeout=3600,
        result_ttl=86400,
    )


def obter_job(job_id: str) -> Any | None:
    if Job is None:
        return None

    conexao = obter_conexao_redis()
    if conexao is None:
        return None

    try:
        return Job.fetch(job_id, connection=conexao)
    except Exception as erro:
        logger.warning(
            "Nao foi possivel carregar job da fila",
            extra={"job_id": job_id, "erro": str(erro)},
        )
        return None
