from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else ROOT_DIR


def _ler_lista_csv(nome: str, padrao: list[str]) -> list[str]:
    valor = os.getenv(nome, "").strip()
    if not valor:
        return padrao

    itens = [item.strip() for item in valor.split(",")]
    return [item for item in itens if item]


def _caminhos_env() -> list[Path]:
    return [APP_DIR, ROOT_DIR, Path.cwd()]


def _carregar_arquivo_env(candidato: Path) -> None:
    if not candidato.is_file():
        return

    for linha in candidato.read_text(encoding="utf-8").splitlines():
        texto = linha.strip()
        if not texto or texto.startswith("#") or "=" not in texto:
            continue

        chave, valor = texto.split("=", 1)
        chave = chave.strip()
        valor = valor.strip().strip('"').strip("'")
        if chave and chave not in os.environ:
            os.environ[chave] = valor


def _carregar_env_basico() -> None:
    for base in _caminhos_env():
        _carregar_arquivo_env(base / ".env")
        _carregar_arquivo_env(base / ".env.local")


def _detectar_ambiente_bruto() -> str:
    valor = (
        os.getenv("HELPER_ENV")
        or os.getenv("APP_ENV")
        or os.getenv("NODE_ENV")
        or ""
    ).strip().lower()

    if valor in {"development", "dev", "local"}:
        return "development"
    if valor in {"production", "prod"}:
        return "production"

    tem_producao = any((base / ".env.production").is_file() for base in _caminhos_env())
    tem_desenvolvimento = any((base / ".env.development").is_file() for base in _caminhos_env())
    if tem_producao and not tem_desenvolvimento:
        return "production"
    if tem_desenvolvimento and not tem_producao:
        return "development"

    backend_preconfigurado = (
        os.getenv("BACKEND_URL")
        or os.getenv("PRODUCTION_BACKEND_URL")
        or os.getenv("DEV_BACKEND_URL")
        or ""
    ).strip()
    if backend_preconfigurado and "localhost" not in backend_preconfigurado and "127.0.0.1" not in backend_preconfigurado:
        return "production"

    return "development"


def _carregar_env_especifico(ambiente: str) -> None:
    sufixo = ".env.production" if ambiente == "production" else ".env.development"
    for base in _caminhos_env():
        _carregar_arquivo_env(base / sufixo)


_carregar_env_basico()
ENVIRONMENT = _detectar_ambiente_bruto()
_carregar_env_especifico(ENVIRONMENT)


def _resolver_backend_url() -> str:
    if ENVIRONMENT == "production":
        valor = (
            os.getenv("BACKEND_URL")
            or os.getenv("PRODUCTION_BACKEND_URL")
            or ""
        ).strip()
        if not valor:
            raise RuntimeError(
                "Configure BACKEND_URL ou PRODUCTION_BACKEND_URL para production.",
            )
        return valor.rstrip("/")

    valor = (
        os.getenv("BACKEND_URL")
        or os.getenv("DEV_BACKEND_URL")
        or "http://localhost:8000"
    ).strip()
    return valor.rstrip("/")


def obter_backend_url() -> str:
    return _resolver_backend_url()


BACKEND_URL = obter_backend_url()
HELPER_VERSION = "1.0.9"
PORTAL_URL = "https://www.portaldoservidor.mg.gov.br/"
UPLOAD_ENDPOINT = os.getenv(
    "UPLOAD_ENDPOINT",
    "/api/financeiro/importacao-temporaria/upload-lote",
).strip()
IMPORT_TOKEN_HEADER = os.getenv("IMPORT_TOKEN_HEADER", "X-Import-Token").strip()
DOWNLOAD_TIMEOUT_MS = int(os.getenv("DOWNLOAD_TIMEOUT_MS", "15000"))
BROWSER_TIMEOUT_MS = int(os.getenv("BROWSER_TIMEOUT_MS", "30000"))
UPLOAD_TIMEOUT_SECONDS = int(os.getenv("UPLOAD_TIMEOUT_SECONDS", "120"))
DOWNLOAD_ROOT = Path(
    os.getenv("DOWNLOAD_ROOT", str(APP_DIR / "tmp")),
).expanduser().resolve()

DOWNLOAD_SELECTORS = _ler_lista_csv(
    "DOWNLOAD_SELECTORS",
    [
        "button:has-text('Baixar')",
        "a:has-text('Baixar')",
        "button:has-text('Download')",
        "a:has-text('Download')",
        "button[aria-label*='baix' i]",
        "a[aria-label*='baix' i]",
        "[title*='baix' i]",
        "[title*='download' i]",
        "a[download]",
        "button[download]",
        "a[href$='.pdf' i]",
        "a[href*='.pdf?' i]",
    ],
)

DOWNLOAD_KEYWORDS = ("baix", "download", "pdf", "salvar", "exportar")
