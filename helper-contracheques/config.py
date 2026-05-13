from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent


def _ler_lista_csv(nome: str, padrao: list[str]) -> list[str]:
    valor = os.getenv(nome, "").strip()
    if not valor:
        return padrao

    itens = [item.strip() for item in valor.split(",")]
    return [item for item in itens if item]


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").strip().rstrip("/")
PORTAL_URL = os.getenv("PORTAL_URL", "https://www.gov.br/").strip().rstrip("/")
UPLOAD_ENDPOINT = os.getenv(
    "UPLOAD_ENDPOINT",
    "/api/financeiro/importacao-temporaria/upload-lote",
).strip()
IMPORT_TOKEN_HEADER = os.getenv("IMPORT_TOKEN_HEADER", "X-Import-Token").strip()
DOWNLOAD_TIMEOUT_MS = int(os.getenv("DOWNLOAD_TIMEOUT_MS", "15000"))
BROWSER_TIMEOUT_MS = int(os.getenv("BROWSER_TIMEOUT_MS", "30000"))
UPLOAD_TIMEOUT_SECONDS = int(os.getenv("UPLOAD_TIMEOUT_SECONDS", "120"))
DOWNLOAD_ROOT = Path(
    os.getenv("DOWNLOAD_ROOT", str(ROOT_DIR / "tmp")),
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

