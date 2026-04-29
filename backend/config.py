from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

for candidato in (
    BASE_DIR / ".env",
    PROJECT_ROOT / ".env",
    Path.cwd() / ".env",
    Path.cwd() / "backend" / ".env",
):
    if candidato.is_file():
        load_dotenv(candidato, override=False)
        break


def _ler_lista_csv(nome_variavel: str) -> list[str]:
    valor = os.getenv(nome_variavel, "")
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

        for base in (
            BASE_DIR,
            PROJECT_ROOT,
            Path.cwd(),
            Path.cwd() / "backend",
        ):
            candidato = (base / caminho).resolve()
            if candidato.exists():
                return candidato

        caminho = (BASE_DIR / caminho).resolve()
    return caminho


HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
CORS_ORIGINS = _ler_lista_csv("CORS_ORIGINS") or ["http://localhost:3000"]
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000").rstrip("/")
EMAIL_CONFIRMATION_SUBJECT = os.getenv(
    "EMAIL_CONFIRMATION_SUBJECT",
    "Confirme seu cadastro",
).strip()
EMAIL_RECOVERY_SUBJECT = os.getenv(
    "EMAIL_RECOVERY_SUBJECT",
    "Redefina sua senha",
).strip()
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME).strip()
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Gestao de Carreira").strip()
SMTP_USE_TLS = _ler_bool("SMTP_USE_TLS", True)
SMTP_USE_SSL = _ler_bool("SMTP_USE_SSL", False)
