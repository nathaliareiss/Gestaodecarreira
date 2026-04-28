from __future__ import annotations

import hashlib
from secrets import token_urlsafe


def gerar_hash_sha256(valor: str) -> str:
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()


def gerar_token_seguro(tamanho: int = 32) -> str:
    return token_urlsafe(tamanho)
