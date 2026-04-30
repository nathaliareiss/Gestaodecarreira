from __future__ import annotations

from time import perf_counter

from backend.database.database import SessionLocal
from backend.logger import logger
from backend.metrics import registrar_job_execucao
from backend.schemas.historico_funcional_schema import (
    AfastamentosUploadRequest,
    HistoricoFuncionalUploadRequest,
)
from backend.services.historico_funcional_job_service import (
    processar_afastamentos_db,
    processar_historico_funcional_db,
)


def processar_historico_funcional_job(dados: dict) -> dict:
    inicio = perf_counter()
    payload = HistoricoFuncionalUploadRequest.model_validate(dados)
    logger.info(
        "Worker processando historico funcional",
        extra={"usuario_id": payload.usuario_id, "arquivo_nome": payload.arquivo_nome},
    )
    try:
        with SessionLocal() as db:
            resposta = processar_historico_funcional_db(db, payload)
            return resposta.model_dump(mode="json")
    finally:
        registrar_job_execucao(
            "historico_funcional",
            "finished",
            perf_counter() - inicio,
        )


def processar_afastamentos_job(usuario_id: int, dados: dict) -> dict:
    inicio = perf_counter()
    payload = AfastamentosUploadRequest.model_validate(dados)
    logger.info(
        "Worker processando afastamentos",
        extra={"usuario_id": usuario_id, "arquivo_nome": payload.arquivo_nome},
    )
    try:
        with SessionLocal() as db:
            resposta = processar_afastamentos_db(db, usuario_id, payload)
            return resposta.model_dump(mode="json")
    finally:
        registrar_job_execucao(
            "afastamentos",
            "finished",
            perf_counter() - inicio,
        )
