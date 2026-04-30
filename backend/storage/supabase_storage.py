from __future__ import annotations

import os
import re
from pathlib import PurePosixPath
from pathlib import Path
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

LOCAL_STORAGE_ROOT = Path(os.getenv("STORAGE_LOCAL_DIR", str(Path(__file__).resolve().parent.parent / "storage_data")))


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


def _caminho_local(caminho_storage: str) -> Path:
    return LOCAL_STORAGE_ROOT / caminho_storage


def _salvar_localmente(conteudo_pdf: bytes, caminho_storage: str) -> str:
    caminho = _caminho_local(caminho_storage)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(conteudo_pdf)
    logger.warning(
        "Arquivo salvo no storage local de fallback",
        extra={"storage_path": caminho_storage, "local_path": str(caminho)},
    )
    return caminho_storage


def _arquivo_local_existe(caminho_storage: str) -> bool:
    return _caminho_local(caminho_storage).is_file()


def obter_origem_storage(caminho_storage: str) -> str:
    return "local" if _arquivo_local_existe(caminho_storage) else "supabase"


def enviar_pdf_para_storage(
    conteudo_pdf: bytes,
    caminho_storage: str,
    content_type: str = "application/pdf",
) -> str:
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        assert SUPABASE_URL
        url = f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/{SUPABASE_STORAGE_BUCKET}/{caminho_storage}"
        headers = _headers()
        headers.update(
            {
                "Content-Type": content_type,
                "x-upsert": "false",
            }
        )
        try:
            resposta = requests.post(url, headers=headers, data=conteudo_pdf, timeout=60)
            if resposta.ok:
                return caminho_storage

            logger.warning(
                "Supabase Storage recusou o upload, usando fallback local",
                extra={"storage_path": caminho_storage, "status_code": resposta.status_code},
            )
        except Exception as erro:
            logger.warning(
                "Falha ao enviar arquivo para o Supabase Storage, usando fallback local",
                extra={"storage_path": caminho_storage, "erro": str(erro)},
            )

    return _salvar_localmente(conteudo_pdf, caminho_storage)


def baixar_pdf_storage(caminho_storage: str) -> bytes:
    if _arquivo_local_existe(caminho_storage):
        return _caminho_local(caminho_storage).read_bytes()

    _validar_configuracao()

    assert SUPABASE_URL
    url = f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/{SUPABASE_STORAGE_BUCKET}/{caminho_storage}"
    try:
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
    except StorageError:
        raise
    except Exception as erro:
        logger.error(
            "Falha ao acessar o Supabase Storage",
            extra={"storage_path": caminho_storage, "erro": str(erro)},
        )
        raise StorageError("Nao foi possivel acessar o storage do Supabase no momento.") from erro
