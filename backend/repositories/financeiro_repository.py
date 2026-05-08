from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from backend.database.models import PayrollBatch, Paycheck, PaycheckItem


def criar_lote_financeiro(
    db: Session,
    user_id: int | None,
    total_files: int,
) -> PayrollBatch:
    lote = PayrollBatch(
        user_id=user_id,
        total_files=total_files,
        processed_files=0,
        failed_files=0,
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


def atualizar_lote_financeiro(
    db: Session,
    lote: PayrollBatch,
    *,
    processed_delta: int = 0,
    failed_delta: int = 0,
    status: str | None = None,
) -> PayrollBatch:
    lote.processed_files += processed_delta
    lote.failed_files += failed_delta
    if status is not None:
        lote.status = status
    db.add(lote)
    db.commit()
    db.refresh(lote)
    return lote


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
