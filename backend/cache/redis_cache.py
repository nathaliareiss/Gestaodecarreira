from __future__ import annotations

import json
import random
from typing import Any

from backend.logger import logger
from backend.queue.queue_config import obter_conexao_redis

CACHE_NAMESPACE = "cache:v1"
CACHE_TTL_USUARIO_ULTIMO_SEGUNDOS = 300
CACHE_TTL_HISTORICO_ULTIMO_SEGUNDOS = 600


def _cliente_redis():
    return obter_conexao_redis()


def _chave(*partes: str) -> str:
    return ":".join((CACHE_NAMESPACE, *partes))


def _ttl_com_jitter(ttl_segundos: int) -> int:
    return max(30, int(ttl_segundos * random.uniform(0.85, 1.15)))


def chave_usuario_ultimo() -> str:
    return _chave("usuarios", "ultimo")


def chave_historico_ultimo_usuario(usuario_id: int) -> str:
    return _chave("historicos", "ultimo", "usuario", str(usuario_id))


def obter_json_cache(chave: str) -> dict[str, Any] | None:
    cliente = _cliente_redis()
    if cliente is None:
        return None

    try:
        valor = cliente.get(chave)
        if valor is None:
            return None
        if isinstance(valor, bytes):
            valor = valor.decode("utf-8")
        return json.loads(valor)
    except Exception as erro:
        logger.warning("Falha ao ler cache Redis", extra={"cache_key": chave, "erro": str(erro)})
        return None


def definir_json_cache(chave: str, valor: Any, ttl_segundos: int) -> None:
    cliente = _cliente_redis()
    if cliente is None:
        return

    try:
        cliente.setex(
            chave,
            _ttl_com_jitter(ttl_segundos),
            json.dumps(valor, ensure_ascii=False, separators=(",", ":")),
        )
    except Exception as erro:
        logger.warning("Falha ao gravar cache Redis", extra={"cache_key": chave, "erro": str(erro)})


def invalidar_cache(chave: str) -> None:
    cliente = _cliente_redis()
    if cliente is None:
        return

    try:
        cliente.delete(chave)
    except Exception as erro:
        logger.warning("Falha ao invalidar cache Redis", extra={"cache_key": chave, "erro": str(erro)})

