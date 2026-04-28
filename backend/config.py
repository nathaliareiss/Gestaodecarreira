from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def _ler_lista_csv(nome_variavel: str) -> list[str]:
    valor = os.environ[nome_variavel]
    return [item.strip() for item in valor.split(",") if item.strip()]


def _ler_bool(nome_variavel: str, padrao: bool = False) -> bool:
    valor = os.getenv(nome_variavel)
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "yes", "on"}


def _resolver_caminho_env(nome_variavel: str, padrao: Path) -> Path:
    valor = os.getenv(nome_variavel)
    if not valor:
        return padrao

    caminho = Path(valor).expanduser()
    if not caminho.is_absolute():
        if caminho.exists():
            return caminho.resolve()

        candidato_raiz = (BASE_DIR.parent / caminho).resolve()
        if candidato_raiz.exists():
            return candidato_raiz

        caminho = (BASE_DIR / caminho).resolve()
    return caminho


HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
CORS_ORIGINS = _ler_lista_csv("CORS_ORIGINS")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000").rstrip("/")
EMAIL_CONFIRMATION_SUBJECT = os.getenv(
    "EMAIL_CONFIRMATION_SUBJECT",
    "Confirme seu cadastro",
).strip()
GOOGLE_GMAIL_SCOPES = ("https://www.googleapis.com/auth/gmail.send",)
GOOGLE_GMAIL_CLIENT_FILE = _resolver_caminho_env(
    "GOOGLE_GMAIL_CLIENT_FILE",
    BASE_DIR / "google_client_secret.json",
)
GOOGLE_GMAIL_TOKEN_FILE = _resolver_caminho_env(
    "GOOGLE_GMAIL_TOKEN_FILE",
    BASE_DIR / "google_token.json",
)
