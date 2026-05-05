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


HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
REDIS_URL = os.getenv("REDIS_URL", "").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "gestaocarreira").strip()
SUPABASE_STORAGE_HISTORICO_PREFIX = os.getenv(
    "SUPABASE_STORAGE_HISTORICO_PREFIX",
    "historicofuncional",
).strip()
SUPABASE_STORAGE_AFASTAMENTOS_PREFIX = os.getenv(
    "SUPABASE_STORAGE_AFASTAMENTOS_PREFIX",
    "afastamentos",
).strip()
CORS_ORIGINS = _ler_lista_csv("CORS_ORIGINS")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "").rstrip("/")
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
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USER).strip()
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Gestao de Carreira").strip()
SMTP_USE_TLS = _ler_bool("SMTP_USE_TLS", True)
SMTP_USE_SSL = _ler_bool("SMTP_USE_SSL", False)
AUTO_SYNC_DB_SCHEMA = _ler_bool("AUTO_SYNC_DB_SCHEMA", False)
