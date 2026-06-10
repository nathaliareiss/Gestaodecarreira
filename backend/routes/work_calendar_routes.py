from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.schemas.work_calendar_schema import (
    VacationPeriodCreateRequest,
    VacationPeriodResponse,
    WorkCalendarEventResponse,
    WorkCalendarOverrideCreateRequest,
    WorkCalendarOverrideResponse,
    WorkScheduleCreateRequest,
    WorkScheduleResponse,
)
from backend.services.auth_service import obter_usuario_autenticado
from backend.services.work_calendar_service import (
    criar_escala_trabalho,
    criar_excecao_calendario,
    criar_periodo_ferias,
    gerar_eventos_calendario,
    listar_escalas_trabalho,
    listar_excecoes_calendario,
    listar_periodos_ferias,
)

router = APIRouter(tags=["work-calendar"])


@router.post("/work-schedules", response_model=WorkScheduleResponse, status_code=status.HTTP_201_CREATED)
def post_work_schedule(
    payload: WorkScheduleCreateRequest,
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> WorkScheduleResponse:
    try:
        return criar_escala_trabalho(db, current_user.id, payload)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro)) from erro


@router.get("/work-schedules", response_model=list[WorkScheduleResponse])
def get_work_schedules(
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> list[WorkScheduleResponse]:
    return listar_escalas_trabalho(db, current_user.id)


@router.post("/vacations", response_model=VacationPeriodResponse, status_code=status.HTTP_201_CREATED)
def post_vacation(
    payload: VacationPeriodCreateRequest,
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> VacationPeriodResponse:
    try:
        return criar_periodo_ferias(db, current_user.id, payload)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro)) from erro


@router.get("/vacations", response_model=list[VacationPeriodResponse])
def get_vacations(
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> list[VacationPeriodResponse]:
    return listar_periodos_ferias(db, current_user.id)


@router.post("/calendar-overrides", response_model=WorkCalendarOverrideResponse, status_code=status.HTTP_201_CREATED)
def post_calendar_override(
    payload: WorkCalendarOverrideCreateRequest,
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> WorkCalendarOverrideResponse:
    return criar_excecao_calendario(db, current_user.id, payload)


@router.get("/calendar-overrides", response_model=list[WorkCalendarOverrideResponse])
def get_calendar_overrides(
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> list[WorkCalendarOverrideResponse]:
    return listar_excecoes_calendario(db, current_user.id)


@router.get("/calendar/events", response_model=list[WorkCalendarEventResponse])
def get_calendar_events(
    start: date = Query(...),
    end: date = Query(...),
    current_user=Depends(obter_usuario_autenticado),
    db: Session = Depends(get_db),
) -> list[WorkCalendarEventResponse]:
    try:
        return gerar_eventos_calendario(db, current_user.id, start, end)
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro)) from erro
