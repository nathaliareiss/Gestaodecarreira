from __future__ import annotations

import os
from decimal import Decimal
from time import perf_counter

from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.database.models import Paycheck, PaycheckItem
from backend.logger import logger
from backend.metrics import registrar_job_execucao
from backend.repositories.financeiro_repository import (
    atualizar_lote_financeiro,
    existe_paycheck_por_competencia,
    obter_lote_financeiro_por_id,
    salvar_paycheck_com_itens,
)
from backend.schemas.financeiro_schema import LoteFinanceiroJobPayload
from backend.services.contracheque_parser import (
    extrair_rubricas_contracheque,
    parse_contracheque,
)

ZERO = Decimal("0.00")


def _para_decimal(valor: object) -> Decimal:
    if isinstance(valor, Decimal):
        return valor

    if valor is None or valor == "":
        return ZERO

    return Decimal(str(valor))


def _criar_paycheck_item(payload: dict[str, object]) -> PaycheckItem:
    return PaycheckItem(
        tipo=str(payload["tipo"]),
        descricao=str(payload["descricao"]),
        valor=_para_decimal(payload["valor"]),
    )


def _criar_paycheck_model(
    batch_id: int,
    user_id: int | None,
    dados: dict[str, object],
) -> Paycheck:
    competencia = str(dados.get("competencia") or "").strip()
    ano = int(dados.get("ano") or 0)
    mes = int(dados.get("mes") or 0)

    if not competencia or ano <= 0 or mes <= 0:
        raise ValueError("Nao foi possivel identificar a competencia do contracheque.")

    return Paycheck(
        batch_id=batch_id,
        user_id=user_id,
        competencia=competencia,
        ano=ano,
        mes=mes,
        bruto=_para_decimal(dados.get("bruto")),
        descontos=_para_decimal(dados.get("descontos")),
        liquido=_para_decimal(dados.get("liquido")),
        vencimento_basico=_para_decimal(dados.get("vencimento_basico")),
        adicional_desempenho=_para_decimal(dados.get("adicional_desempenho")),
        adicional_noturno=_para_decimal(dados.get("adicional_noturno")),
        irrf=_para_decimal(dados.get("irrf")),
        previdencia=_para_decimal(dados.get("previdencia")),
    )


def _processar_arquivo_individual(
    db: Session,
    batch_id: int,
    user_id: int | None,
    arquivo_nome: str,
    caminho_temporario: str,
) -> None:
    dados = parse_contracheque(caminho_temporario)
    rubricas = extrair_rubricas_contracheque(caminho_temporario)
    paycheck = _criar_paycheck_model(batch_id, user_id, dados)

    if user_id is not None and existe_paycheck_por_competencia(db, user_id, paycheck.competencia):
        raise ValueError(
            f"Já existe um contracheque salvo para a competência {paycheck.competencia}."
        )

    itens = [_criar_paycheck_item(item) for item in rubricas]
    salvar_paycheck_com_itens(db, paycheck, itens)
    logger.info(
        "Contracheque financeiro salvo",
        extra={
            "batch_id": batch_id,
            "arquivo_nome": arquivo_nome,
            "competencia": paycheck.competencia,
        },
    )


def processar_lote_financeiro_job(dados: dict) -> dict[str, object]:
    inicio = perf_counter()
    payload = LoteFinanceiroJobPayload.model_validate(dados)
    status_job = "finished"

    try:
        with SessionLocal() as db:
            lote = obter_lote_financeiro_por_id(db, payload.batch_id)
            if lote is None:
                raise ValueError("Lote financeiro nao encontrado.")

            atualizar_lote_financeiro(db, lote, status="processing")

            for arquivo in payload.arquivos:
                try:
                    _processar_arquivo_individual(
                        db=db,
                        batch_id=payload.batch_id,
                        user_id=payload.user_id,
                        arquivo_nome=arquivo.arquivo_nome,
                        caminho_temporario=arquivo.arquivo_temporario_path,
                    )
                    atualizar_lote_financeiro(db, lote, processed_delta=1)
                except Exception as erro_arquivo:
                    db.rollback()
                    logger.warning(
                        "Falha ao processar contracheque do lote",
                        extra={
                            "batch_id": payload.batch_id,
                            "arquivo_nome": arquivo.arquivo_nome,
                            "erro": str(erro_arquivo),
                        },
                    )
                    atualizar_lote_financeiro(db, lote, failed_delta=1)
                finally:
                    try:
                        os.unlink(arquivo.arquivo_temporario_path)
                    except FileNotFoundError:
                        pass

            lote_atualizado = obter_lote_financeiro_por_id(db, payload.batch_id)
            if lote_atualizado is not None:
                status_final = "failed" if lote_atualizado.processed_files == 0 else "completed"
                atualizar_lote_financeiro(db, lote_atualizado, status=status_final)

            lote_final = obter_lote_financeiro_por_id(db, payload.batch_id)
            if lote_final is None:
                raise ValueError("Lote financeiro nao encontrado.")

            return {
                "batch_id": lote_final.id,
                "total": lote_final.total_files,
                "processed": lote_final.processed_files,
                "failed": lote_final.failed_files,
                "status": lote_final.status,
            }
    except Exception:
        status_job = "failed"
        raise
    finally:
        registrar_job_execucao(
            "financeiro_lote",
            status_job,
            perf_counter() - inicio,
        )
