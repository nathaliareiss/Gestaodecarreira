from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

import requests

from config import BACKEND_URL, IMPORT_TOKEN_HEADER, UPLOAD_ENDPOINT, UPLOAD_TIMEOUT_SECONDS


@dataclass(frozen=True)
class UploadResultado:
    batch_id: int | None
    status: str
    raw: dict[str, object]


class UploadError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None, detail: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


def _extrair_mensagem_erro(response: requests.Response, fallback: str) -> str:
    try:
        payload = response.json()
    except Exception:
        return fallback

    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str) and detail.strip():
            return detail.strip()

    return fallback


def upload_pdfs_para_backend(
    pdf_paths: Iterable[Path],
    import_token: str,
    *,
    backend_url: str | None = None,
    upload_endpoint: str | None = None,
) -> UploadResultado:
    url_base = backend_url.rstrip("/") if backend_url else BACKEND_URL
    endpoint = upload_endpoint or UPLOAD_ENDPOINT
    url = urljoin(f"{url_base}/", endpoint if endpoint.startswith("/") else f"/{endpoint}")

    arquivos_abertos: list[tuple[str, tuple[str, object, str]]] = []
    handles: list[object] = []
    try:
        for caminho in pdf_paths:
            arquivo = Path(caminho)
            handle = arquivo.open("rb")
            handles.append(handle)
            arquivos_abertos.append(
                (
                    "arquivos",
                    (
                        arquivo.name,
                        handle,
                        "application/pdf",
                    ),
                )
            )

        resposta = requests.post(
            url,
            headers={IMPORT_TOKEN_HEADER: import_token},
            files=arquivos_abertos,
            timeout=UPLOAD_TIMEOUT_SECONDS,
        )

        if not resposta.ok:
            mensagem = _extrair_mensagem_erro(
                resposta,
                "Falha ao enviar PDFs para o backend.",
            )
            raise UploadError(
                mensagem,
                status_code=resposta.status_code,
                detail=mensagem,
            )

        payload = resposta.json()
        if not isinstance(payload, dict):
            raise UploadError("Resposta inesperada do backend ao enviar PDFs.")

        return UploadResultado(
            batch_id=payload.get("batch_id") if isinstance(payload.get("batch_id"), int) else None,
            status=str(payload.get("status") or "unknown"),
            raw=payload,
        )
    finally:
        for handle in handles:
            try:
                handle.close()
            except Exception:
                pass
