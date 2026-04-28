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
        caminho = (BASE_DIR / caminho).resolve()
    return caminho


def _localizar_arquivo_client_secret() -> Path:
    valor_env = os.getenv("GOOGLE_GMAIL_CLIENT_FILE")
    if valor_env:
        caminho = Path(valor_env).expanduser()
        if not caminho.is_absolute():
            caminho = (BASE_DIR / caminho).resolve()
        return caminho

    candidatos = sorted(BASE_DIR.glob("client_secret_*.json"))
    if candidatos:
        return candidatos[0]

    return BASE_DIR / "client_secret.json"


HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
CORS_ORIGINS = _ler_lista_csv("CORS_ORIGINS")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000").rstrip("/")
EMAIL_CONFIRMATION_SUBJECT = os.getenv(
    "EMAIL_CONFIRMATION_SUBJECT",
    "Confirme seu cadastro",
).strip()
GOOGLE_GMAIL_SCOPES = ("https://www.googleapis.com/auth/gmail.send",)
GOOGLE_GMAIL_CLIENT_FILE = _localizar_arquivo_client_secret()
GOOGLE_GMAIL_TOKEN_FILE = _resolver_caminho_env(
    "GOOGLE_GMAIL_TOKEN_FILE",
    BASE_DIR / "google_token.json",
)
