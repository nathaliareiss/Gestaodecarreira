from __future__ import annotations

import os
from pathlib import Path

from backend.env_loader import carregar_primeiro_env

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

ENV_LOAD_RESULT = carregar_primeiro_env((
    BASE_DIR / ".env",
    PROJECT_ROOT / ".env",
    Path.cwd() / ".env",
    Path.cwd() / "backend" / ".env",
))


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
STORAGE_HISTORICO_PREFIX = os.getenv(
    "STORAGE_HISTORICO_PREFIX",
    "historicofuncional",
).strip()
STORAGE_AFASTAMENTOS_PREFIX = os.getenv(
    "STORAGE_AFASTAMENTOS_PREFIX",
    "afastamentos",
).strip()
CORS_ORIGINS = _ler_lista_csv("CORS_ORIGINS")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "").rstrip("/")
EMAIL_CONFIRMATION_SUBJECT = os.getenv(
    "EMAIL_CONFIRMATION_SUBJECT",
    "Confirme seu cadastro no Career Flow",
).strip()
EMAIL_RECOVERY_SUBJECT = os.getenv(
    "EMAIL_RECOVERY_SUBJECT",
    "Redefina sua senha no Career Flow",
).strip()
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
SMTP_FROM = os.getenv("SMTP_FROM", "").strip()
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_FROM or SMTP_USER).strip()
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Career Flow").strip()
SMTP_USE_TLS = _ler_bool("SMTP_USE_TLS", True)
SMTP_USE_SSL = _ler_bool("SMTP_USE_SSL", False)
SMTP_TIMEOUT = int(os.getenv("SMTP_TIMEOUT", "10"))
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "auto").strip().lower()
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", SMTP_FROM_EMAIL or SMTP_USER).strip()
AUTO_SYNC_DB_SCHEMA = _ler_bool("AUTO_SYNC_DB_SCHEMA", False)
SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
PRIVACY_POLICY_VERSION = os.getenv("PRIVACY_POLICY_VERSION", "2026-06-10").strip() or "2026-06-10"
