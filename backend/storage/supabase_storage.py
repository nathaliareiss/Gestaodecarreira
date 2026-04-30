from __future__ import annotations

import re
from pathlib import PurePosixPath
from uuid import uuid4

import requests

from backend.config import (
    SUPABASE_SERVICE_ROLE_KEY,
    SUPABASE_STORAGE_AFASTAMENTOS_PREFIX,
    SUPABASE_STORAGE_BUCKET,
    SUPABASE_STORAGE_HISTORICO_PREFIX,
    SUPABASE_URL,
)
from backend.logger import logger


class StorageError(RuntimeError):
    pass


def _validar_configuracao() -> None:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise StorageError(
            "Configure SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY para usar o Storage do Supabase."
        )


def _normalizar_nome_arquivo(nome_arquivo: str | None) -> str:
    nome = PurePosixPath(nome_arquivo or "arquivo.pdf").name
    nome = re.sub(r"[^A-Za-z0-9._-]+", "_", nome).strip("._-")
    return nome or "arquivo.pdf"


def _montar_caminho(prefixo: str, nome_arquivo: str, identificador: int | None) -> str:
    pasta = [prefixo]
    if identificador is not None:
        pasta.append(str(identificador))
    pasta.append(f"{uuid4().hex}-{_normalizar_nome_arquivo(nome_arquivo)}")
    return "/".join(pasta)


def gerar_caminho_storage_historico(
    nome_arquivo: str,
    usuario_id: int | None,
) -> str:
    return _montar_caminho(SUPABASE_STORAGE_HISTORICO_PREFIX, nome_arquivo, usuario_id)


def gerar_caminho_storage_afastamentos(
    nome_arquivo: str,
    usuario_id: int | None,
) -> str:
    return _montar_caminho(SUPABASE_STORAGE_AFASTAMENTOS_PREFIX, nome_arquivo, usuario_id)


def _headers() -> dict[str, str]:
    _validar_configuracao()
    assert SUPABASE_SERVICE_ROLE_KEY
    return {
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
    }


def enviar_pdf_para_storage(
    conteudo_pdf: bytes,
    caminho_storage: str,
    content_type: str = "application/pdf",
) -> str:
    _validar_configuracao()

    assert SUPABASE_URL
    url = f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/{SUPABASE_STORAGE_BUCKET}/{caminho_storage}"
    headers = _headers()
    headers.update(
        {
            "Content-Type": content_type,
            "x-upsert": "false",
        }
    )
    resposta = requests.post(url, headers=headers, data=conteudo_pdf, timeout=60)
    if not resposta.ok:
        logger.error(
            "Falha ao enviar arquivo para o Supabase Storage",
            extra={"storage_path": caminho_storage, "status_code": resposta.status_code},
        )
        raise StorageError(
            f"Nao foi possivel enviar o arquivo para o storage ({resposta.status_code})."
        )

    return caminho_storage


def baixar_pdf_storage(caminho_storage: str) -> bytes:
    _validar_configuracao()

    assert SUPABASE_URL
    url = f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/{SUPABASE_STORAGE_BUCKET}/{caminho_storage}"
    resposta = requests.get(url, headers=_headers(), timeout=60)
    if not resposta.ok:
        logger.error(
            "Falha ao baixar arquivo do Supabase Storage",
            extra={"storage_path": caminho_storage, "status_code": resposta.status_code},
        )
        raise StorageError(
            f"Nao foi possivel baixar o arquivo do storage ({resposta.status_code})."
        )

    return resposta.content
