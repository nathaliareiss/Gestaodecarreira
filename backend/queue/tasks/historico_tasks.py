from __future__ import annotations

from backend.database.database import SessionLocal
from backend.logger import logger
from backend.schemas.historico_funcional_schema import (
    AfastamentosUploadRequest,
    HistoricoFuncionalUploadRequest,
)
from backend.services.historico_funcional_job_service import (
    processar_afastamentos_db,
    processar_historico_funcional_db,
)


def processar_historico_funcional_job(dados: dict) -> dict:
    payload = HistoricoFuncionalUploadRequest.model_validate(dados)
    logger.info(
        "Worker processando historico funcional",
        extra={"usuario_id": payload.usuario_id, "arquivo_nome": payload.arquivo_nome},
    )
    with SessionLocal() as db:
        resposta = processar_historico_funcional_db(db, payload)
        return resposta.model_dump(mode="json")


def processar_afastamentos_job(usuario_id: int, dados: dict) -> dict:
    payload = AfastamentosUploadRequest.model_validate(dados)
    logger.info(
        "Worker processando afastamentos",
        extra={"usuario_id": usuario_id, "arquivo_nome": payload.arquivo_nome},
    )
    with SessionLocal() as db:
        resposta = processar_afastamentos_db(db, usuario_id, payload)
        return resposta.model_dump(mode="json")
