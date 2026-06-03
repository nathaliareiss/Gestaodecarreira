from __future__ import annotations

import hashlib
import json
import os
import uuid
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Header, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.logger import logger
from backend.queue.queue_config import obter_fila_financeiro
from backend.queue.tasks.financeiro_tasks import (
    processar_arquivo_financeiro_job,
    processar_lote_financeiro_job,
)
from backend.repositories.financeiro_repository import (
    atualizar_lote_financeiro,
    criar_lote_financeiro,
    obter_paychecks_por_batch_id,
    marcar_importacao_temporaria_como_usada,
    obter_lote_financeiro_por_id,
    obter_paychecks_por_usuario_id,
    remover_contracheques_salvos_por_usuario,
)
from backend.schemas.financeiro_schema import (
    ArquivoFinanceiroJobPayload,
    ContrachequeResumoResponse,
    EvolucaoSalarialResponse,
    FinanceiroImportacaoTemporariaCriacaoResponse,
    FinanceiroImportacaoTemporariaValidacaoRequest,
    FinanceiroImportacaoTemporariaValidacaoResponse,
    LoteFinanceiroJobPayload,
    LoteFinanceiroStatusResponse,
    LoteFinanceiroUploadResponse,
)
from backend.services.contracheque_parser import parse_contracheque
from backend.services.financeiro_importacao_service import (
    criar_importacao_temporaria_financeira,
    validar_importacao_temporaria_financeira,
)
from backend.services.financeiro_batch_service import (
    calcular_evolucao_salarial_lote,
    calcular_evolucao_salarial_por_usuario,
    detectar_competencias_faltantes_por_paychecks,
)
from backend.services.auth_service import obter_usuario_autenticado

router = APIRouter(prefix="/financeiro", tags=["financeiro"])


def _serializar_valor(valor):
    if isinstance(valor, Decimal):
        return format(valor, "f")

    return valor


def _serializar_contracheque(dados: dict[str, object]) -> dict[str, object]:
    return {chave: _serializar_valor(valor) for chave, valor in dados.items()}


def _gerar_hash_conteudo(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def _arquivo_pdf_valido(conteudo: bytes) -> bool:
    return bool(conteudo and conteudo.lstrip().startswith(b"%PDF"))


def _nome_arquivo_seguro(nome: str | None, fallback: str) -> str:
    candidato = Path(nome or fallback).name.strip()
    return candidato or fallback


def _diretorio_temporario_financeiro() -> Path:
    diretorio = Path(__file__).resolve().parents[1] / "temp_data" / "financeiro"
    diretorio.mkdir(parents=True, exist_ok=True)
    return diretorio


def _carregar_mensagens_erro_lote(valor_bruto: str | None) -> list[str]:
    if not valor_bruto:
        return []

    try:
        mensagens = json.loads(valor_bruto)
    except Exception:
        return []

    if not isinstance(mensagens, list):
        return []

    return [str(mensagem).strip() for mensagem in mensagens if str(mensagem).strip()]


def _carregar_competencias_faltantes_lote(valor_bruto: str | None) -> list[str]:
    if not valor_bruto:
        return []

    try:
        competencias = json.loads(valor_bruto)
    except Exception:
        return []

    if not isinstance(competencias, list):
        return []

    return [str(item).strip() for item in competencias if str(item).strip()]


def _serializar_paycheck_resumo(paycheck) -> ContrachequeResumoResponse:
    return ContrachequeResumoResponse(
        id=paycheck.id,
        competencia=paycheck.competencia,
        ano=paycheck.ano,
        mes=paycheck.mes,
        salario_base=float(paycheck.vencimento_basico),
        bruto_total=float(paycheck.bruto),
        liquido=float(paycheck.liquido),
        descontos=float(paycheck.descontos),
    )


async def _processar_upload_lote_financeiro(
    *,
    arquivos: list[UploadFile],
    user_id: int,
    db: Session,
    missing_competencies: list[str] | None = None,
    background_tasks: BackgroundTasks | None = None,
) -> LoteFinanceiroUploadResponse:
    if not arquivos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie ao menos um PDF valido.",
        )

    lote = None
    diretorio_temporario = _diretorio_temporario_financeiro() / f"batch_{uuid.uuid4().hex}"
    diretorio_temporario.mkdir(parents=True, exist_ok=True)
    arquivos_job: list[dict[str, str]] = []
    agendado = False

    try:
        for indice, arquivo in enumerate(arquivos, start=1):
            conteudo = await arquivo.read()
            if not _arquivo_pdf_valido(conteudo):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Envie apenas arquivos PDF validos.",
                )

            nome_arquivo = _nome_arquivo_seguro(arquivo.filename, f"contracheque-{indice}.pdf")
            caminho = diretorio_temporario / f"{indice:03d}_{nome_arquivo}"
            caminho.write_bytes(conteudo)
            arquivos_job.append(
                {
                    "arquivo_nome": nome_arquivo,
                    "arquivo_temporario_path": str(caminho),
                    "file_hash": _gerar_hash_conteudo(conteudo),
                }
            )

        lote = criar_lote_financeiro(db, user_id, len(arquivos_job), missing_competencies=missing_competencies)
        fila = obter_fila_financeiro()
        payload = LoteFinanceiroJobPayload(
            batch_id=lote.id,
            user_id=user_id,
            arquivos=arquivos_job,
        )
        payload_json = payload.model_dump(mode="json")

        if fila is not None:
            try:
                job_ids: list[str] = []
                for arquivo_job in arquivos_job:
                    payload_arquivo = ArquivoFinanceiroJobPayload(
                        batch_id=lote.id,
                        user_id=user_id,
                        arquivo=arquivo_job,
                    )
                    job = fila.enqueue(
                        processar_arquivo_financeiro_job,
                        payload_arquivo.model_dump(mode="json"),
                        job_timeout=1800,
                    )
                    job_ids.append(job.id)
                agendado = True
                logger.info(
                    "Lote financeiro agendado",
                    extra={
                        "batch_id": lote.id,
                        "job_ids": job_ids,
                        "total_files": lote.total_files,
                        "jobs_enfileirados": len(job_ids),
                        "estrategia": "um_job_por_pdf",
                    },
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
                atualizar_lote_financeiro(db, lote, status="failed")
                logger.exception(
                    "Falha ao agendar os arquivos do lote financeiro",
                    extra={
                        "batch_id": lote.id,
                        "total_files": lote.total_files,
                        "estrategia": "um_job_por_pdf",
                        "erro": str(erro_fila),
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Nao foi possivel agendar os arquivos do lote financeiro no momento.",
                ) from erro_fila

        logger.warning(
            "Fila financeira indisponivel, processando lote financeiro diretamente",
            extra={
                "batch_id": lote.id,
                "total_files": lote.total_files,
                "estrategia": "um_job_por_pdf",
            },
        )

        if background_tasks is not None:
            background_tasks.add_task(processar_lote_financeiro_job, payload_json)
            agendado = True
            try:
                atualizar_lote_financeiro(db, lote, status="processing")
            except Exception as erro_status:
                logger.warning(
                    "Nao foi possivel atualizar o status do lote financeiro",
                    extra={"batch_id": lote.id, "erro": str(erro_status)},
                )
            return LoteFinanceiroUploadResponse(batch_id=lote.id, status="processing")

        resultado_direto = processar_lote_financeiro_job(payload_json)
        return LoteFinanceiroUploadResponse(
            batch_id=int(resultado_direto["batch_id"]),
            status=str(resultado_direto["status"]),
        )
    except HTTPException:
        if lote is not None:
            atualizar_lote_financeiro(db, lote, status="failed")
        raise
    except Exception as erro:
        if lote is not None:
            atualizar_lote_financeiro(db, lote, status="failed")
        logger.exception(
            "Falha ao agendar ou processar lote financeiro",
            extra={"batch_id": getattr(lote, "id", None), "erro": str(erro)},
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
    "/importacao-temporaria",
    response_model=FinanceiroImportacaoTemporariaCriacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_importacao_temporaria_financeira_route(
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> FinanceiroImportacaoTemporariaCriacaoResponse:
    importacao = criar_importacao_temporaria_financeira(db, current_user)
    return FinanceiroImportacaoTemporariaCriacaoResponse(
        token=importacao.token,
        expires_at=importacao.importacao.expires_at,
        scope=importacao.importacao.scope,
    )


@router.post(
    "/importacao-temporaria/validar",
    response_model=FinanceiroImportacaoTemporariaValidacaoResponse,
)
def validar_importacao_temporaria_financeira_route(
    payload: FinanceiroImportacaoTemporariaValidacaoRequest,
    db: Session = Depends(get_db),
) -> FinanceiroImportacaoTemporariaValidacaoResponse:
    try:
        importacao = validar_importacao_temporaria_financeira(db, payload.token)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(erro),
        ) from erro

    return FinanceiroImportacaoTemporariaValidacaoResponse(
        valid=True,
        scope=importacao.scope,
        user_id=importacao.user_id,
        expires_at=importacao.expires_at,
        used=importacao.used_at is not None,
    )


@router.post(
    "/importacao-temporaria/upload-lote",
    response_model=LoteFinanceiroUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_lote_financeiro_importacao_temporaria(
    background_tasks: BackgroundTasks,
    arquivos: list[UploadFile] = File(...),
    x_import_token: str = Header(..., alias="X-Import-Token"),
    missing_competencies: str = Form("[]"),
    db: Session = Depends(get_db),
) -> LoteFinanceiroUploadResponse:
    try:
        importacao = validar_importacao_temporaria_financeira(db, x_import_token)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(erro),
        ) from erro

    resposta = await _processar_upload_lote_financeiro(
        arquivos=arquivos,
        user_id=importacao.user_id,
        db=db,
        missing_competencies=_carregar_competencias_faltantes_lote(missing_competencies),
        background_tasks=background_tasks,
    )
    marcar_importacao_temporaria_como_usada(db, importacao)
    return resposta


@router.post(
    "/upload-lote",
    response_model=LoteFinanceiroUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_lote_financeiro(
    background_tasks: BackgroundTasks,
    arquivos: list[UploadFile] = File(...),
    current_user=Depends(obter_usuario_autenticado),
    missing_competencies: str = Form("[]"),
    db: Session = Depends(get_db),
) -> LoteFinanceiroUploadResponse:
    return await _processar_upload_lote_financeiro(
        arquivos=arquivos,
        user_id=current_user.id,
        db=db,
        missing_competencies=_carregar_competencias_faltantes_lote(missing_competencies),
        background_tasks=background_tasks,
    )


@router.get("/batch/{batch_id}", response_model=LoteFinanceiroStatusResponse)
def obter_status_lote_financeiro(
    batch_id: int,
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> LoteFinanceiroStatusResponse:
    lote = obter_lote_financeiro_por_id(db, batch_id)
    if lote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote financeiro nao encontrado.",
        )
    if lote.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Voce nao tem acesso a este lote financeiro.",
        )

    competencias_faltantes = _carregar_competencias_faltantes_lote(getattr(lote, "missing_competencies", None))

    return LoteFinanceiroStatusResponse(
        total=lote.total_files,
        processed_count=lote.processed_files,
        duplicated_count=lote.duplicated_files,
        failed_count=lote.failed_files,
        status=lote.status,
        last_error_message=lote.last_error_message or None,
        failure_messages=_carregar_mensagens_erro_lote(lote.failure_messages),
        missing_competencies=(
            competencias_faltantes
            if competencias_faltantes
            else (
                detectar_competencias_faltantes_por_paychecks(obter_paychecks_por_batch_id(db, batch_id))
                if lote.status in {"completed", "failed"}
                else []
            )
        ),
        processed=lote.processed_files,
        duplicated=lote.duplicated_files,
        failed=lote.failed_files,
    )


@router.get("/evolucao-salarial", response_model=EvolucaoSalarialResponse)
def obter_evolucao_salarial_persistida(
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> EvolucaoSalarialResponse:
    evolucao = calcular_evolucao_salarial_por_usuario(db, current_user.id)
    return EvolucaoSalarialResponse.model_validate(evolucao)


@router.get("/batch/{batch_id}/evolucao-salarial", response_model=EvolucaoSalarialResponse)
def obter_evolucao_salarial_lote(
    batch_id: int,
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> EvolucaoSalarialResponse:
    lote = obter_lote_financeiro_por_id(db, batch_id)
    if lote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote financeiro nao encontrado.",
        )
    if lote.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Voce nao tem acesso a este lote financeiro.",
        )

    try:
        evolucao = calcular_evolucao_salarial_lote(db, batch_id)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum contracheque processado foi encontrado para este lote.",
        ) from erro

    return EvolucaoSalarialResponse.model_validate(evolucao)


@router.get("/contracheques", response_model=list[ContrachequeResumoResponse])
def listar_contracheques_salvos(
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> list[ContrachequeResumoResponse]:
    paychecks = obter_paychecks_por_usuario_id(db, current_user.id)
    return [_serializar_paycheck_resumo(paycheck) for paycheck in paychecks]


@router.delete("/contracheques")
def limpar_contracheques_salvos(
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    resultado = remover_contracheques_salvos_por_usuario(db, current_user.id)
    logger.info(
        "Contracheques salvos apagados",
        extra={
            "user_id": current_user.id,
            "deleted_batches": resultado["deleted_batches"],
            "deleted_paychecks": resultado["deleted_paychecks"],
        },
    )
    return resultado
