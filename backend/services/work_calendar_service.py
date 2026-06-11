from __future__ import annotations

import json
from datetime import date

import holidays
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from backend.database.models import VacationPeriod, WorkCalendarOverride, WorkSchedule
from backend.repositories.work_calendar_repository import (
    criar_vacation_period,
    criar_work_calendar_override,
    criar_work_schedule,
    desativar_escalas_ativas_do_usuario,
    listar_vacations_por_usuario,
    listar_vacations_por_usuario_no_intervalo,
    listar_work_calendar_overrides_por_usuario,
    listar_work_calendar_overrides_por_usuario_no_intervalo,
    listar_work_schedules_por_usuario,
    obter_work_schedule_ativo_por_usuario,
)
from backend.schemas.work_calendar_schema import (
    VacationPeriodCreateRequest,
    VacationPeriodResponse,
    WorkCalendarEventResponse,
    WorkCalendarOverrideCreateRequest,
    WorkCalendarOverrideResponse,
    WorkScheduleCreateRequest,
    WorkScheduleResponse,
)

CORES_EVENTO = {
    "work": "#14b8a6",
    "off": "#94a3b8",
    "vacation": "#f59e0b",
    "premium_vacation": "#38bdf8",
    "holiday": "#ef4444",
    "exception": "#8b5cf6",
}

MUNICIPAL_HOLIDAYS: dict[tuple[str, str], dict[tuple[int, int], str]] = {
    ("MG", "belo horizonte"): {
        (8, 15): "Feriado municipal - Nossa Senhora da Boa Viagem",
        (12, 8): "Feriado municipal - Imaculada Conceicao",
    },
    ("MG", "contagem"): {
        (8, 30): "Feriado municipal - Aniversario de Contagem",
        (12, 8): "Feriado municipal - Imaculada Conceicao",
    },
    ("MG", "betim"): {
        (7, 16): "Feriado municipal - Nossa Senhora do Carmo",
    },
    ("MG", "uberlandia"): {
        (8, 31): "Feriado municipal - Aniversario de Uberlandia",
    },
    ("MG", "juiz de fora"): {
        (6, 13): "Feriado municipal - Santo Antonio",
    },
    ("SP", "sao paulo"): {
        (1, 25): "Feriado municipal - Aniversario de Sao Paulo",
        (11, 20): "Feriado municipal - Dia da Consciencia Negra",
    },
    ("RJ", "rio de janeiro"): {
        (1, 20): "Feriado municipal - Sao Sebastiao",
        (4, 23): "Feriado municipal - Sao Jorge",
    },
}


def _serializar_lista_json(value: list[int] | list[bool]) -> str:
    return json.dumps(value, ensure_ascii=False)


def _desserializar_int_list(value: str | None) -> list[int]:
    if not value:
        return []
    try:
        loaded = json.loads(value)
    except Exception:
        return []
    if not isinstance(loaded, list):
        return []
    return [int(item) for item in loaded if int(item) in {0, 1, 2, 3, 4, 5, 6}]


def _desserializar_bool_list(value: str | None) -> list[bool]:
    if not value:
        return []
    try:
        loaded = json.loads(value)
    except Exception:
        return []
    if not isinstance(loaded, list):
        return []
    return [bool(item) for item in loaded]


def _validar_schedule_payload(payload: WorkScheduleCreateRequest) -> None:
    if payload.schedule_type == "5x2" and not payload.working_weekdays:
        payload.working_weekdays = [0, 1, 2, 3, 4]

    if payload.schedule_type == "custom" and not payload.custom_pattern:
        raise ValueError("Informe um padrao personalizado com ao menos um dia.")

    if payload.schedule_type != "custom":
        payload.custom_pattern = []

    if payload.schedule_type != "5x2":
        payload.working_weekdays = []

    if payload.state_code:
        payload.state_code = payload.state_code.strip().upper()[:2]

    if payload.city_name:
        payload.city_name = payload.city_name.strip()


def _schedule_to_response(schedule: WorkSchedule) -> WorkScheduleResponse:
    return WorkScheduleResponse(
        id=schedule.id,
        user_id=schedule.user_id,
        name=schedule.name,
        schedule_type=schedule.schedule_type,  # type: ignore[arg-type]
        anchor_date=schedule.anchor_date,
        state_code=schedule.state_code,
        city_name=schedule.city_name,
        working_weekdays=_desserializar_int_list(schedule.working_weekdays_json),
        custom_pattern=_desserializar_bool_list(schedule.custom_pattern_json),
        note=schedule.note,
        is_active=bool(schedule.is_active),
        created_at=schedule.created_at,
        updated_at=schedule.updated_at,
    )


def _vacation_to_response(vacation: VacationPeriod) -> VacationPeriodResponse:
    return VacationPeriodResponse(
        id=vacation.id,
        user_id=vacation.user_id,
        title=vacation.title,
        vacation_type=getattr(vacation, "vacation_type", "regular"),  # type: ignore[arg-type]
        start_date=vacation.start_date,
        end_date=vacation.end_date,
        requested_days=vacation.requested_days,
        counted_days=vacation.counted_days,
        note=vacation.note,
        created_at=vacation.created_at,
        updated_at=vacation.updated_at,
    )


def _override_to_response(override: WorkCalendarOverride) -> WorkCalendarOverrideResponse:
    return WorkCalendarOverrideResponse(
        id=override.id,
        user_id=override.user_id,
        override_date=override.override_date,
        is_working_day=bool(override.is_working_day),
        title=override.title,
        note=override.note,
        created_at=override.created_at,
        updated_at=override.updated_at,
    )


def criar_escala_trabalho(
    db: Session,
    user_id: int,
    payload: WorkScheduleCreateRequest,
) -> WorkScheduleResponse:
    _validar_schedule_payload(payload)
    if payload.is_active:
        desativar_escalas_ativas_do_usuario(db, user_id)

    schedule = WorkSchedule(
        user_id=user_id,
        name=payload.name.strip(),
        schedule_type=payload.schedule_type,
        anchor_date=payload.anchor_date,
        state_code=payload.state_code,
        city_name=payload.city_name,
        working_weekdays_json=_serializar_lista_json(payload.working_weekdays),
        custom_pattern_json=_serializar_lista_json(payload.custom_pattern),
        note=payload.note.strip() if payload.note else None,
        is_active=payload.is_active,
    )
    return _schedule_to_response(criar_work_schedule(db, schedule))


def listar_escalas_trabalho(db: Session, user_id: int) -> list[WorkScheduleResponse]:
    return [_schedule_to_response(item) for item in listar_work_schedules_por_usuario(db, user_id)]


def criar_periodo_ferias(
    db: Session,
    user_id: int,
    payload: VacationPeriodCreateRequest,
) -> VacationPeriodResponse:
    schedule = obter_work_schedule_ativo_por_usuario(db, user_id)
    requested_days = payload.requested_days

    if payload.vacation_type == "regular":
        requested_days = requested_days or 15
        if requested_days not in {10, 15}:
            raise ValueError("Ferias regulamentares devem ser divididas em periodos de 10 ou 15 dias uteis.")
        end_date = _calcular_data_final_ferias_uteis(payload.start_date, requested_days, schedule)
        counted_days = requested_days
    else:
        requested_days = requested_days or 15
        end_date = payload.end_date or (payload.start_date + relativedelta(days=requested_days - 1))
        counted_days = (end_date - payload.start_date).days + 1

    if end_date < payload.start_date:
        raise ValueError("A data final das ferias nao pode ser anterior a data inicial.")

    vacation = VacationPeriod(
        user_id=user_id,
        title=payload.title.strip(),
        vacation_type=payload.vacation_type,
        start_date=payload.start_date,
        end_date=end_date,
        requested_days=requested_days,
        counted_days=counted_days,
        note=payload.note.strip() if payload.note else None,
    )
    return _vacation_to_response(criar_vacation_period(db, vacation))


def listar_periodos_ferias(db: Session, user_id: int) -> list[VacationPeriodResponse]:
    return [_vacation_to_response(item) for item in listar_vacations_por_usuario(db, user_id)]


def criar_excecao_calendario(
    db: Session,
    user_id: int,
    payload: WorkCalendarOverrideCreateRequest,
) -> WorkCalendarOverrideResponse:
    override = WorkCalendarOverride(
        user_id=user_id,
        override_date=payload.override_date,
        is_working_day=payload.is_working_day,
        title=payload.title.strip(),
        note=payload.note.strip() if payload.note else None,
    )
    return _override_to_response(criar_work_calendar_override(db, override))


def listar_excecoes_calendario(db: Session, user_id: int) -> list[WorkCalendarOverrideResponse]:
    return [_override_to_response(item) for item in listar_work_calendar_overrides_por_usuario(db, user_id)]


def _is_work_day(schedule: WorkSchedule, target_date: date) -> bool:
    if target_date < schedule.anchor_date:
        return False

    if schedule.schedule_type == "12x36":
        offset_days = (target_date - schedule.anchor_date).days
        return offset_days % 2 == 0

    if schedule.schedule_type == "24x72":
        offset_days = (target_date - schedule.anchor_date).days
        return offset_days % 4 == 0

    if schedule.schedule_type == "5x2":
        weekdays = _desserializar_int_list(schedule.working_weekdays_json) or [0, 1, 2, 3, 4]
        return target_date.weekday() in weekdays

    pattern = _desserializar_bool_list(schedule.custom_pattern_json)
    if not pattern:
        return False

    offset_days = (target_date - schedule.anchor_date).days
    return pattern[offset_days % len(pattern)]


def _iterar_datas(start_date: date, end_date: date):
    cursor = start_date
    while cursor <= end_date:
        yield cursor
        cursor = cursor + relativedelta(days=1)


def _normalizar_cidade(city_name: str | None) -> str:
    return (city_name or "").strip().lower()


def _feriados_para_escala(schedule: WorkSchedule | None, start_date: date, end_date: date) -> dict[date, str]:
    years = range(start_date.year, end_date.year + 1)
    state_code = (getattr(schedule, "state_code", None) or "").strip().upper() or None
    city_name = _normalizar_cidade(getattr(schedule, "city_name", None))
    holiday_calendar = holidays.country_holidays("BR", subdiv=state_code, years=years)
    result: dict[date, str] = {
        item_date: str(name)
        for item_date, name in holiday_calendar.items()
        if start_date <= item_date <= end_date
    }

    if state_code and city_name:
        for (month, day), name in MUNICIPAL_HOLIDAYS.get((state_code, city_name), {}).items():
            for year in years:
                holiday_date = date(year, month, day)
                if start_date <= holiday_date <= end_date:
                    result[holiday_date] = name

    return result


def _is_business_day(target_date: date, schedule: WorkSchedule | None) -> bool:
    if target_date.weekday() >= 5:
        return False

    return target_date not in _feriados_para_escala(schedule, target_date, target_date)


def _calcular_data_final_ferias_uteis(start_date: date, requested_days: int, schedule: WorkSchedule | None) -> date:
    counted_days = 0
    cursor = start_date

    while True:
        if _is_business_day(cursor, schedule):
            counted_days += 1
            if counted_days == requested_days:
                return cursor

        cursor = cursor + relativedelta(days=1)


def gerar_eventos_calendario(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date,
) -> list[WorkCalendarEventResponse]:
    if end_date < start_date:
        raise ValueError("A data final nao pode ser anterior a data inicial.")

    schedule = obter_work_schedule_ativo_por_usuario(db, user_id)
    vacations = listar_vacations_por_usuario_no_intervalo(db, user_id, start_date, end_date)
    overrides = listar_work_calendar_overrides_por_usuario_no_intervalo(db, user_id, start_date, end_date)
    holiday_calendar = _feriados_para_escala(schedule, start_date, end_date)

    vacations_by_day: dict[date, VacationPeriod] = {}
    for vacation in vacations:
        for vacation_day in _iterar_datas(vacation.start_date, vacation.end_date):
            if start_date <= vacation_day <= end_date:
                vacations_by_day[vacation_day] = vacation

    overrides_by_day = {item.override_date: item for item in overrides}
    events: list[WorkCalendarEventResponse] = []

    for current_day in _iterar_datas(start_date, end_date):
        override = overrides_by_day.get(current_day)
        vacation = vacations_by_day.get(current_day)
        holiday_name = holiday_calendar.get(current_day)

        if vacation is not None:
            events.append(
                WorkCalendarEventResponse(
                    id=f"vacation-{vacation.id}-{current_day.isoformat()}",
                    title=vacation.title,
                    start=current_day,
                    end=current_day + relativedelta(days=1),
                    category="premium_vacation" if getattr(vacation, "vacation_type", "regular") == "premium" else "vacation",
                    color=CORES_EVENTO[
                        "premium_vacation" if getattr(vacation, "vacation_type", "regular") == "premium" else "vacation"
                    ],
                    text_color="#08111d",
                    source="vacation_periods",
                    is_working_day=False,
                )
            )
            continue

        if override is not None:
            events.append(
                WorkCalendarEventResponse(
                    id=f"override-{override.id}",
                    title=override.title,
                    start=current_day,
                    end=current_day + relativedelta(days=1),
                    category="exception",
                    color=CORES_EVENTO["exception"],
                    text_color="#f8fafc",
                    source="work_calendar_overrides",
                    is_working_day=bool(override.is_working_day),
                )
            )
            continue

        is_working_day = _is_work_day(schedule, current_day) if schedule is not None else False
        events.append(
            WorkCalendarEventResponse(
                id=f"base-{current_day.isoformat()}",
                title="Plantao" if is_working_day else "Folga",
                start=current_day,
                end=current_day + relativedelta(days=1),
                category="work" if is_working_day else "off",
                color=CORES_EVENTO["work"] if is_working_day else CORES_EVENTO["off"],
                text_color="#08111d" if is_working_day else "#0f172a",
                source="work_schedules" if schedule is not None else "calendar",
                is_working_day=is_working_day,
            )
        )

        if holiday_name:
            events.append(
                WorkCalendarEventResponse(
                    id=f"holiday-{current_day.isoformat()}",
                    title=str(holiday_name),
                    start=current_day,
                    end=current_day + relativedelta(days=1),
                    category="holiday",
                    color=CORES_EVENTO["holiday"],
                    text_color="#ffffff",
                    source="holidays",
                    is_working_day=is_working_day,
                )
            )

    return events
