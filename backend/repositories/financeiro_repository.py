from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from backend.database.models import PayrollBatch, Paycheck, PaycheckItem


def _para_decimal(valor: int | float | Decimal | None) -> Decimal:
    if isinstance(valor, Decimal):
        return valor

    if valor is None:
        return Decimal("0")

    return Decimal(str(valor))


def criar_lote_financeiro(
    db: Session,
    user_id: int | None,
    total_files: int,
) -> PayrollBatch:
    lote = PayrollBatch(
        user_id=user_id,
        total_files=total_files,
        processed_files=0,
        duplicated_files=0,
        failed_files=0,
        processing_seconds_total=0,
        status="pending",
    )
    db.add(lote)
    db.commit()
    db.refresh(lote)
    return lote


def obter_lote_financeiro_por_id(db: Session, batch_id: int) -> PayrollBatch | None:
    return db.get(PayrollBatch, batch_id)


def obter_paychecks_por_batch_id(db: Session, batch_id: int) -> list[Paycheck]:
    stmt = (
        select(Paycheck)
        .options(selectinload(Paycheck.items))
        .where(Paycheck.batch_id == batch_id)
        .order_by(Paycheck.ano.asc(), Paycheck.mes.asc(), Paycheck.created_at.asc(), Paycheck.id.asc())
    )
    return list(db.scalars(stmt).all())


def obter_paychecks_por_usuario_id(db: Session, user_id: int) -> list[Paycheck]:
    stmt = (
        select(Paycheck)
        .options(selectinload(Paycheck.items))
        .where(Paycheck.user_id == user_id)
        .order_by(Paycheck.ano.asc(), Paycheck.mes.asc(), Paycheck.created_at.asc(), Paycheck.id.asc())
    )
    return list(db.scalars(stmt).all())


def listar_contracheques_resumidos_por_usuario_id(db: Session, user_id: int) -> list[Paycheck]:
    return obter_paychecks_por_usuario_id(db, user_id)


def atualizar_lote_financeiro(
    db: Session,
    lote: PayrollBatch,
    *,
    processed_delta: int = 0,
    duplicated_delta: int = 0,
    failed_delta: int = 0,
    processing_seconds_delta: int | float | Decimal = 0,
    status: str | None = None,
) -> PayrollBatch:
    lote_atual = db.scalar(
        select(PayrollBatch).where(PayrollBatch.id == lote.id).with_for_update()
    )
    if lote_atual is None:
        raise ValueError("Lote financeiro nao encontrado.")

    lote_atual.processed_files += processed_delta
    lote_atual.duplicated_files += duplicated_delta
    lote_atual.failed_files += failed_delta
    lote_atual.processing_seconds_total = _para_decimal(lote_atual.processing_seconds_total) + _para_decimal(
        processing_seconds_delta
    )

    total_tratados = (
        lote_atual.processed_files + lote_atual.duplicated_files + lote_atual.failed_files
    )

    if status is not None:
        lote_atual.status = status
    elif lote_atual.total_files > 0 and total_tratados >= lote_atual.total_files:
        lote_atual.status = "failed" if lote_atual.processed_files == 0 and lote_atual.duplicated_files == 0 else "completed"
    else:
        lote_atual.status = "processing"

    db.add(lote_atual)
    db.commit()
    db.refresh(lote_atual)
    return lote_atual


def existe_paycheck_por_competencia(
    db: Session,
    user_id: int | None,
    competencia: str,
) -> bool:
    stmt = select(Paycheck.id).where(
        Paycheck.user_id == user_id,
        Paycheck.competencia == competencia,
    )
    return db.scalar(stmt) is not None


def existe_paycheck_por_file_hash(
    db: Session,
    user_id: int | None,
    file_hash: str,
) -> bool:
    if not file_hash:
        return False

    stmt = select(Paycheck.id).where(
        Paycheck.user_id == user_id,
        Paycheck.file_hash == file_hash,
    )
    return db.scalar(stmt) is not None


def existe_paycheck_por_chave_negocio(
    db: Session,
    user_id: int | None,
    ano: int,
    mes: int,
    matricula: str,
) -> bool:
    matricula_normalizada = (matricula or "").strip()
    stmt = select(Paycheck.id).where(
        Paycheck.user_id == user_id,
        Paycheck.ano == ano,
        Paycheck.mes == mes,
        Paycheck.matricula == matricula_normalizada,
    )
    return db.scalar(stmt) is not None


def salvar_paycheck_com_itens(
    db: Session,
    paycheck: Paycheck,
    itens: list[PaycheckItem],
) -> Paycheck:
    db.add(paycheck)
    db.flush()

    for item in itens:
        item.paycheck_id = paycheck.id
        db.add(item)

    db.commit()
    db.refresh(paycheck)
    return paycheck
