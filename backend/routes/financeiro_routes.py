from __future__ import annotations

import os
import uuid
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.logger import logger
from backend.queue.queue_config import obter_fila_financeiro
from backend.queue.tasks.financeiro_tasks import processar_lote_financeiro_job
from backend.repositories.financeiro_repository import (
    atualizar_lote_financeiro,
    criar_lote_financeiro,
    obter_lote_financeiro_por_id,
)
from backend.schemas.financeiro_schema import (
    LoteFinanceiroJobPayload,
    LoteFinanceiroStatusResponse,
    LoteFinanceiroUploadResponse,
)
from backend.services.contracheque_parser import parse_contracheque

router = APIRouter(prefix="/financeiro", tags=["financeiro"])


def _serializar_valor(valor):
    if isinstance(valor, Decimal):
        return format(valor, "f")

    return valor


def _serializar_contracheque(dados: dict[str, object]) -> dict[str, object]:
    return {chave: _serializar_valor(valor) for chave, valor in dados.items()}


def _arquivo_pdf_valido(conteudo: bytes) -> bool:
    return bool(conteudo and conteudo.lstrip().startswith(b"%PDF"))


def _nome_arquivo_seguro(nome: str | None, fallback: str) -> str:
    candidato = Path(nome or fallback).name.strip()
    return candidato or fallback


def _diretorio_temporario_financeiro() -> Path:
    diretorio = Path(__file__).resolve().parents[1] / "temp_data" / "financeiro"
    diretorio.mkdir(parents=True, exist_ok=True)
    return diretorio


@router.post("/contracheque/analisar")
async def analisar_contracheque(arquivo: UploadFile = File(...)) -> dict[str, object]:
    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel ler o arquivo enviado.",
        )

    if not conteudo.lstrip().startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie um arquivo PDF valido.",
        )

    caminho_temporario = None
    try:
        caminho_temporario = _diretorio_temporario_financeiro() / f"analisar_{uuid.uuid4().hex}.pdf"
        caminho_temporario.write_bytes(conteudo)

        dados = parse_contracheque(str(caminho_temporario))
        return _serializar_contracheque(dados)
    except HTTPException:
        raise
    except Exception as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel analisar o contracheque. Verifique o PDF e tente novamente.",
        ) from erro
    finally:
        if caminho_temporario:
            try:
                os.unlink(caminho_temporario)
            except FileNotFoundError:
                pass


@router.post(
    "/upload-lote",
    response_model=LoteFinanceiroUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_lote_financeiro(
    arquivos: list[UploadFile] = File(...),
    user_id: int | None = Form(None),
    db: Session = Depends(get_db),
) -> LoteFinanceiroUploadResponse:
    if not arquivos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie ao menos um PDF valido.",
        )

    arquivos_em_memoria: list[tuple[str, bytes]] = []
    for indice, arquivo in enumerate(arquivos, start=1):
        conteudo = await arquivo.read()
        if not _arquivo_pdf_valido(conteudo):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Envie apenas arquivos PDF validos.",
            )

        arquivos_em_memoria.append(
            (
                _nome_arquivo_seguro(arquivo.filename, f"contracheque-{indice}.pdf"),
                conteudo,
            )
        )

    lote = criar_lote_financeiro(db, user_id, len(arquivos_em_memoria))
    fila = obter_fila_financeiro()

    diretorio_temporario = _diretorio_temporario_financeiro() / f"batch_{lote.id}_{uuid.uuid4().hex}"
    diretorio_temporario.mkdir(parents=True, exist_ok=True)
    arquivos_job: list[dict[str, str]] = []
    agendado = False

    try:
        for indice, (nome_arquivo, conteudo) in enumerate(arquivos_em_memoria, start=1):
            caminho = diretorio_temporario / f"{indice:03d}_{nome_arquivo}"
            with caminho.open("wb") as arquivo_saida:
                arquivo_saida.write(conteudo)
            arquivos_job.append(
                {
                    "arquivo_nome": nome_arquivo,
                    "arquivo_temporario_path": str(caminho),
                }
            )

        payload = LoteFinanceiroJobPayload(
            batch_id=lote.id,
            user_id=user_id,
            arquivos=arquivos_job,
        )
        payload_json = payload.model_dump(mode="json")

        if fila is not None:
            try:
                job = fila.enqueue(
                    processar_lote_financeiro_job,
                    payload_json,
                    job_timeout=3600,
                )
                agendado = True
                logger.info(
                    "Lote financeiro agendado",
                    extra={"batch_id": lote.id, "job_id": job.id, "total_files": lote.total_files},
                )
                try:
                    atualizar_lote_financeiro(db, lote, status="processing")
                except Exception as erro_status:
                    logger.warning(
                        "Nao foi possivel atualizar o status do lote financeiro",
                        extra={"batch_id": lote.id, "erro": str(erro_status)},
                    )
                return LoteFinanceiroUploadResponse(batch_id=lote.id, status="processing")
            except Exception as erro_fila:
                logger.warning(
                    "Fila indisponivel, processando lote financeiro diretamente",
                    extra={"batch_id": lote.id, "erro": str(erro_fila)},
                )

        else:
            logger.warning(
                "Fila financeira indisponivel, processando lote financeiro diretamente",
                extra={"batch_id": lote.id, "total_files": lote.total_files},
            )

        resultado_direto = processar_lote_financeiro_job(payload_json)
        return LoteFinanceiroUploadResponse(
            batch_id=int(resultado_direto["batch_id"]),
            status=str(resultado_direto["status"]),
        )
    except HTTPException:
        atualizar_lote_financeiro(db, lote, status="failed")
        raise
    except Exception as erro:
        atualizar_lote_financeiro(db, lote, status="failed")
        logger.exception(
            "Falha ao agendar ou processar lote financeiro",
            extra={"batch_id": lote.id, "erro": str(erro)},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nao foi possivel agendar ou processar o lote financeiro no momento.",
        ) from erro
    finally:
        if not agendado:
            for caminho in diretorio_temporario.glob("*"):
                try:
                    caminho.unlink()
                except FileNotFoundError:
                    pass
            try:
                diretorio_temporario.rmdir()
            except OSError:
                pass


@router.get("/batch/{batch_id}", response_model=LoteFinanceiroStatusResponse)
def obter_status_lote_financeiro(
    batch_id: int,
    db: Session = Depends(get_db),
) -> LoteFinanceiroStatusResponse:
    lote = obter_lote_financeiro_por_id(db, batch_id)
    if lote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote financeiro nao encontrado.",
        )

    return LoteFinanceiroStatusResponse(
        total=lote.total_files,
        processed=lote.processed_files,
        failed=lote.failed_files,
        status=lote.status,
    )
