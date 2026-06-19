from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Literal
from uuid import uuid4

from backend.config import STORAGE_AFASTAMENTOS_PREFIX, STORAGE_HISTORICO_PREFIX
from backend.logger import logger

LOCAL_STORAGE_ROOT = Path(
    os.getenv("STORAGE_LOCAL_DIR", str(Path(__file__).resolve().parent.parent / "storage_data"))
)


class StorageError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ResultadoUploadStorage:
    caminho_storage: str
    origem: Literal["local"]


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


def gerar_caminho_storage_historico(nome_arquivo: str, usuario_id: int | None) -> str:
    return _montar_caminho(STORAGE_HISTORICO_PREFIX, nome_arquivo, usuario_id)


def gerar_caminho_storage_afastamentos(nome_arquivo: str, usuario_id: int | None) -> str:
    return _montar_caminho(STORAGE_AFASTAMENTOS_PREFIX, nome_arquivo, usuario_id)


def _caminho_local(caminho_storage: str) -> Path:
    return LOCAL_STORAGE_ROOT / caminho_storage


def enviar_pdf_para_storage(
    conteudo_pdf: bytes,
    caminho_storage: str,
    content_type: str = "application/pdf",
) -> ResultadoUploadStorage:
    caminho = _caminho_local(caminho_storage)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(conteudo_pdf)
    logger.info(
        "Arquivo salvo no storage local",
        extra={"storage_path": caminho_storage, "local_path": str(caminho), "content_type": content_type},
    )
    return ResultadoUploadStorage(caminho_storage, "local")


def baixar_pdf_storage(caminho_storage: str) -> bytes:
    caminho = _caminho_local(caminho_storage)
    if not caminho.is_file():
        raise StorageError("Arquivo nao encontrado no storage local.")
    return caminho.read_bytes()


def obter_origem_storage(caminho_storage: str) -> str:
    return "local"
