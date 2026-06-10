from __future__ import annotations

from datetime import date

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.database.models import VacationPeriod, WorkCalendarOverride, WorkSchedule


def desativar_escalas_ativas_do_usuario(db: Session, user_id: int) -> None:
    db.execute(
        update(WorkSchedule)
        .where(WorkSchedule.user_id == user_id, WorkSchedule.is_active.is_(True))
        .values(is_active=False)
    )


def criar_work_schedule(db: Session, schedule: WorkSchedule) -> WorkSchedule:
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def listar_work_schedules_por_usuario(db: Session, user_id: int) -> list[WorkSchedule]:
    stmt = (
        select(WorkSchedule)
        .where(WorkSchedule.user_id == user_id)
        .order_by(WorkSchedule.is_active.desc(), WorkSchedule.created_at.desc(), WorkSchedule.id.desc())
    )
    return list(db.scalars(stmt).all())


def obter_work_schedule_ativo_por_usuario(db: Session, user_id: int) -> WorkSchedule | None:
    stmt = (
        select(WorkSchedule)
        .where(WorkSchedule.user_id == user_id, WorkSchedule.is_active.is_(True))
        .order_by(WorkSchedule.updated_at.desc(), WorkSchedule.id.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def criar_vacation_period(db: Session, vacation: VacationPeriod) -> VacationPeriod:
    db.add(vacation)
    db.commit()
    db.refresh(vacation)
    return vacation


def listar_vacations_por_usuario(db: Session, user_id: int) -> list[VacationPeriod]:
    stmt = (
        select(VacationPeriod)
        .where(VacationPeriod.user_id == user_id)
        .order_by(VacationPeriod.start_date.desc(), VacationPeriod.id.desc())
    )
    return list(db.scalars(stmt).all())


def listar_vacations_por_usuario_no_intervalo(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date,
) -> list[VacationPeriod]:
    stmt = (
        select(VacationPeriod)
        .where(
            VacationPeriod.user_id == user_id,
            VacationPeriod.start_date <= end_date,
            VacationPeriod.end_date >= start_date,
        )
        .order_by(VacationPeriod.start_date.asc(), VacationPeriod.id.asc())
    )
    return list(db.scalars(stmt).all())


def criar_work_calendar_override(db: Session, override: WorkCalendarOverride) -> WorkCalendarOverride:
    db.add(override)
    db.commit()
    db.refresh(override)
    return override


def listar_work_calendar_overrides_por_usuario(db: Session, user_id: int) -> list[WorkCalendarOverride]:
    stmt = (
        select(WorkCalendarOverride)
        .where(WorkCalendarOverride.user_id == user_id)
        .order_by(WorkCalendarOverride.override_date.desc(), WorkCalendarOverride.id.desc())
    )
    return list(db.scalars(stmt).all())


def listar_work_calendar_overrides_por_usuario_no_intervalo(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date,
) -> list[WorkCalendarOverride]:
    stmt = (
        select(WorkCalendarOverride)
        .where(
            WorkCalendarOverride.user_id == user_id,
            WorkCalendarOverride.override_date >= start_date,
            WorkCalendarOverride.override_date <= end_date,
        )
        .order_by(WorkCalendarOverride.override_date.asc(), WorkCalendarOverride.id.asc())
    )
    return list(db.scalars(stmt).all())

