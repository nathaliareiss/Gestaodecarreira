from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def _ler_lista_csv(nome_variavel: str) -> list[str]:
    valor = os.environ[nome_variavel]
    return [item.strip() for item in valor.split(",") if item.strip()]


HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
CORS_ORIGINS = _ler_lista_csv("CORS_ORIGINS")
