from __future__ import annotations

import json
from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.logger import logger
from backend.services.auth_service import obter_usuario_autenticado
from backend.cache.redis_cache import (
    CACHE_TTL_HISTORICO_ULTIMO_SEGUNDOS,
    chave_historico_ultimo_usuario,
    definir_json_cache,
    obter_json_cache,
)
from backend.repositories.historico_funcional_repository import obter_ultimo_historico_por_usuario
from backend.queue.queue_config import obter_fila_historicos, obter_job
from backend.queue.tasks.historico_tasks import (
    processar_afastamentos_job,
    processar_historico_funcional_job,
)
from backend.schemas.historico_funcional_schema import (
    AfastamentosUploadRequest,
    HistoricoFuncionalResponse,
    HistoricoFuncionalUploadRequest,
)
from backend.schemas.queue_schema import JobAgendadoResponse, JobStatusResponse
from backend.services.historico_funcional_job_service import (
    normalizar_dados_historico_salvo,
    processar_afastamentos_db,
    processar_historico_funcional_db,
)
from backend.storage import (
    StorageError,
    enviar_pdf_para_storage,
    gerar_caminho_storage_afastamentos,
    gerar_caminho_storage_historico,
)

router = APIRouter(prefix="/historicos-funcionais", tags=["historicos-funcionais"])


def _responder_job_agendado(job_id: str, detalhe: str) -> JobAgendadoResponse:
    return JobAgendadoResponse(job_id=job_id, status="queued", detail=detalhe)


def _ler_nome_arquivo(upload: UploadFile, fallback: str) -> str:
    return upload.filename or fallback


async def _armazenar_arquivo_pdf(
    upload: UploadFile,
    caminho_storage: str,
) -> tuple[str, str]:
    conteudo = await upload.read()
    if not isinstance(conteudo, bytes) or not conteudo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel ler o arquivo enviado.",
        )

    try:
        resultado = enviar_pdf_para_storage(conteudo, caminho_storage)
        return resultado.caminho_storage, resultado.origem
    except StorageError as erro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nao foi possivel salvar o arquivo no storage no momento.",
        ) from erro


def _responder_status_job(job_id: str) -> JobStatusResponse:
    job = obter_job(job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A fila de processamento nao esta disponivel no momento.",
        )

    status_job = job.get_status(refresh=True)
    if status_job == "finished":
        return JobStatusResponse(
            job_id=job_id,
            status="finished",
            result=job.result if isinstance(job.result, dict) else None,
        )

    if status_job == "failed":
        logger.error(
            "Job da fila falhou",
            extra={"job_id": job_id, "funcao": getattr(job, "func_name", None)},
        )
        return JobStatusResponse(
            job_id=job_id,
            status="failed",
            detail="Nao foi possivel concluir o processamento em segundo plano.",
        )

    return JobStatusResponse(
        job_id=job_id,
        status="started" if status_job in {"started", "deferred"} else "queued",
    )


@router.post(
    "/analisar",
    response_model=HistoricoFuncionalResponse | JobAgendadoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def analisar_e_salvar_historico(
    arquivo: UploadFile = File(...),
    data_nascimento: date = Form(...),
    anos_clt_averbados: int = Form(0),
    current_user=Depends(obter_usuario_autenticado),
    afastamentos_arquivo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> HistoricoFuncionalResponse | JobAgendadoResponse:
    arquivo_nome = _ler_nome_arquivo(arquivo, "historico-funcional.pdf")
    arquivo_storage_path = gerar_caminho_storage_historico(arquivo_nome, current_user.id)
    arquivo_storage_path, arquivo_armazenamento_origem = await _armazenar_arquivo_pdf(
        arquivo,
        arquivo_storage_path,
    )

    afastamentos_arquivo_nome = None
    afastamentos_storage_path = None
    afastamentos_armazenamento_origem = None
    if afastamentos_arquivo is not None:
        afastamentos_arquivo_nome = _ler_nome_arquivo(afastamentos_arquivo, "afastamentos.pdf")
        afastamentos_storage_path = gerar_caminho_storage_afastamentos(
            afastamentos_arquivo_nome,
            current_user.id,
        )
        afastamentos_storage_path, afastamentos_armazenamento_origem = await _armazenar_arquivo_pdf(
            afastamentos_arquivo,
            afastamentos_storage_path,
        )

    armazenamento_origem = "local"

    dados = HistoricoFuncionalUploadRequest(
        usuario_id=current_user.id,
        arquivo_nome=arquivo_nome,
        arquivo_storage_path=arquivo_storage_path,
        armazenamento_origem=armazenamento_origem,
        data_nascimento=data_nascimento,
        anos_clt_averbados=anos_clt_averbados,
        afastamentos_arquivo_nome=afastamentos_arquivo_nome,
        afastamentos_storage_path=afastamentos_storage_path,
        afastamentos_armazenamento_origem=afastamentos_armazenamento_origem,
    )
    logger.info(
        "Recebido historico funcional para analise",
        extra={
            "usuario_id": current_user.id,
            "arquivo_nome": dados.arquivo_nome,
            "tem_afastamentos": bool(dados.afastamentos_storage_path),
        },
    )

    fila = obter_fila_historicos()
    if fila is not None:
        try:
            job = fila.enqueue(
                processar_historico_funcional_job,
                dados.model_dump(mode="json"),
                job_timeout=900,
            )
            logger.info(
                "Historico funcional agendado na fila",
                extra={
                    "job_id": job.id,
                    "usuario_id": dados.usuario_id,
                    "arquivo_nome": dados.arquivo_nome,
                },
            )
            return _responder_job_agendado(
                job.id,
                "Seu PDF foi recebido e esta sendo processado em segundo plano.",
            )
        except Exception:
            logger.warning(
                "Fila indisponivel, processando historico funcional diretamente",
                extra={"usuario_id": dados.usuario_id, "arquivo_nome": dados.arquivo_nome},
            )
            try:
                return processar_historico_funcional_db(db, dados, processamento_origem="direto")
            except StorageError as erro_storage:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Nao foi possivel acessar o storage para processar o PDF.",
                ) from erro_storage
            except ValueError as erro_valor:
                logger.warning(
                    "Falha ao analisar historico funcional",
                    extra={"usuario_id": dados.usuario_id, "arquivo_nome": dados.arquivo_nome},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nao foi possivel analisar o arquivo enviado. Verifique o PDF e tente novamente.",
                ) from erro_valor
            except Exception as erro_direto:
                logger.exception(
                    "Falha inesperada ao analisar historico funcional sem fila",
                    extra={"usuario_id": dados.usuario_id, "arquivo_nome": dados.arquivo_nome},
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Nao foi possivel analisar o arquivo enviado no momento.",
                ) from erro_direto

    try:
        return processar_historico_funcional_db(db, dados, processamento_origem="direto")
    except StorageError as erro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nao foi possivel acessar o storage para processar o PDF.",
        ) from erro
    except ValueError as erro:
        logger.warning(
            "Falha ao analisar historico funcional",
            extra={"usuario_id": dados.usuario_id, "arquivo_nome": dados.arquivo_nome},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel analisar o arquivo enviado. Verifique o PDF e tente novamente.",
        ) from erro
    except Exception as erro:
        logger.exception(
            "Falha inesperada ao analisar historico funcional",
            extra={"usuario_id": dados.usuario_id, "arquivo_nome": dados.arquivo_nome},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Nao foi possivel analisar o arquivo enviado no momento.",
        ) from erro


@router.post(
    "/usuario/{usuario_id}/afastamentos",
    response_model=HistoricoFuncionalResponse | JobAgendadoResponse,
)
async def anexar_afastamentos_historico(
    usuario_id: int,
    arquivo: UploadFile = File(...),
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> HistoricoFuncionalResponse | JobAgendadoResponse:
    if usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Voce nao tem acesso a este historico funcional.",
        )
    arquivo_nome = _ler_nome_arquivo(arquivo, "afastamentos.pdf")
    arquivo_storage_path = gerar_caminho_storage_afastamentos(arquivo_nome, current_user.id)
    arquivo_storage_path, arquivo_armazenamento_origem = await _armazenar_arquivo_pdf(
        arquivo,
        arquivo_storage_path,
    )

    dados = AfastamentosUploadRequest(
        arquivo_nome=arquivo_nome,
        arquivo_storage_path=arquivo_storage_path,
        armazenamento_origem=arquivo_armazenamento_origem,
    )
    logger.info(
        "Recebido arquivo de afastamentos",
        extra={"user_id": usuario_id, "arquivo_nome": dados.arquivo_nome},
    )

    fila = obter_fila_historicos()
    if fila is not None:
        try:
            job = fila.enqueue(
                processar_afastamentos_job,
                current_user.id,
                dados.model_dump(mode="json"),
                job_timeout=900,
            )
            logger.info(
                "Afastamentos agendados na fila",
                extra={
                    "job_id": job.id,
                    "user_id": usuario_id,
                    "arquivo_nome": dados.arquivo_nome,
                },
            )
            return _responder_job_agendado(
                job.id,
                "Seu PDF de afastamentos foi recebido e esta sendo processado em segundo plano.",
            )
        except Exception:
            logger.warning(
                "Fila indisponivel, processando afastamentos diretamente",
                extra={"user_id": usuario_id, "arquivo_nome": dados.arquivo_nome},
            )
            try:
                return processar_afastamentos_db(db, current_user.id, dados, processamento_origem="direto")
            except StorageError as erro_storage:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Nao foi possivel acessar o storage para processar o PDF.",
                ) from erro_storage
            except ValueError as erro_valor:
                mensagem = str(erro_valor)
                logger.warning(
                    "Falha ao analisar afastamentos",
                    extra={"user_id": usuario_id, "arquivo_nome": dados.arquivo_nome},
                )
                if "Nenhum historico funcional encontrado" in mensagem:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Nenhum historico funcional encontrado para este usuario.",
                    ) from erro_valor
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Nao foi possivel analisar o arquivo de afastamentos. Verifique o PDF e tente novamente.",
                ) from erro_valor
            except Exception as erro_direto:
                logger.exception(
                    "Falha inesperada ao analisar afastamentos sem fila",
                    extra={"user_id": usuario_id, "arquivo_nome": dados.arquivo_nome},
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Nao foi possivel analisar o arquivo de afastamentos no momento.",
                ) from erro_direto

    try:
        return processar_afastamentos_db(db, current_user.id, dados, processamento_origem="direto")
    except StorageError as erro:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nao foi possivel acessar o storage para processar o PDF.",
        ) from erro
    except ValueError as erro:
        mensagem = str(erro)
        logger.warning(
            "Falha ao analisar afastamentos",
            extra={"user_id": usuario_id, "arquivo_nome": dados.arquivo_nome},
        )
        if "Nenhum historico funcional encontrado" in mensagem:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum historico funcional encontrado para este usuario.",
            ) from erro
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel analisar o arquivo de afastamentos. Verifique o PDF e tente novamente.",
        ) from erro
    except Exception as erro:
        logger.exception(
            "Falha inesperada ao analisar afastamentos",
            extra={"user_id": usuario_id, "arquivo_nome": dados.arquivo_nome},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Nao foi possivel analisar o arquivo de afastamentos no momento.",
        ) from erro


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def obter_status_job(job_id: str) -> JobStatusResponse:
    logger.debug("Consultando status do job", extra={"job_id": job_id})
    return _responder_status_job(job_id)


@router.get("/usuario/{usuario_id}/ultimo", response_model=HistoricoFuncionalResponse)
def obter_ultimo_historico_do_usuario(
    usuario_id: int,
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> HistoricoFuncionalResponse:
    if usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Voce nao tem acesso a este historico funcional.",
        )
    logger.debug("Carregando ultimo historico funcional", extra={"user_id": current_user.id})

    cache = obter_json_cache(chave_historico_ultimo_usuario(current_user.id))
    if cache is not None:
        logger.debug("Ultimo historico funcional carregado do cache", extra={"user_id": current_user.id})
        return HistoricoFuncionalResponse.model_validate(cache)

    historico = obter_ultimo_historico_por_usuario(db, current_user.id)
    if historico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum historico funcional encontrado para este usuario.",
        )

    try:
        dados = json.loads(historico.dados_json)
        dados = normalizar_dados_historico_salvo(dados, historico.id, current_user.id)
        resposta = HistoricoFuncionalResponse.model_validate(dados)
        definir_json_cache(
            chave_historico_ultimo_usuario(current_user.id),
            resposta.model_dump(mode="json"),
            CACHE_TTL_HISTORICO_ULTIMO_SEGUNDOS,
        )
        return resposta
    except Exception as erro:
        logger.exception(
            "Falha ao carregar historico funcional salvo",
            extra={"user_id": current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Nao foi possivel carregar o historico funcional salvo.",
        ) from erro
