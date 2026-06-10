from __future__ import annotations

import json
from datetime import date
from types import SimpleNamespace

from backend.services import work_calendar_service


def criar_escala(
    schedule_type: str,
    anchor_date: date,
    *,
    working_weekdays: list[int] | None = None,
    custom_pattern: list[bool] | None = None,
):
    return SimpleNamespace(
        id=1,
        user_id=1,
        schedule_type=schedule_type,
        anchor_date=anchor_date,
        working_weekdays_json=json.dumps(working_weekdays or []),
        custom_pattern_json=json.dumps(custom_pattern or []),
        is_active=True,
    )


def test_is_work_day_para_escala_12x36_alterna_dias() -> None:
    escala = criar_escala("12x36", date(2026, 6, 10))

    assert work_calendar_service._is_work_day(escala, date(2026, 6, 10)) is True
    assert work_calendar_service._is_work_day(escala, date(2026, 6, 11)) is False
    assert work_calendar_service._is_work_day(escala, date(2026, 6, 12)) is True


def test_is_work_day_para_escala_24x72_respeita_ciclo() -> None:
    escala = criar_escala("24x72", date(2026, 6, 10))

    assert work_calendar_service._is_work_day(escala, date(2026, 6, 10)) is True
    assert work_calendar_service._is_work_day(escala, date(2026, 6, 11)) is False
    assert work_calendar_service._is_work_day(escala, date(2026, 6, 14)) is True


def test_is_work_day_para_escala_5x2_usa_dias_configurados() -> None:
    escala = criar_escala("5x2", date(2026, 6, 1), working_weekdays=[0, 1, 2, 3, 4])

    assert work_calendar_service._is_work_day(escala, date(2026, 6, 8)) is True
    assert work_calendar_service._is_work_day(escala, date(2026, 6, 13)) is False


def test_is_work_day_para_escala_personalizada_repete_padrao() -> None:
    escala = criar_escala("custom", date(2026, 6, 10), custom_pattern=[True, True, False])

    assert work_calendar_service._is_work_day(escala, date(2026, 6, 10)) is True
    assert work_calendar_service._is_work_day(escala, date(2026, 6, 11)) is True
    assert work_calendar_service._is_work_day(escala, date(2026, 6, 12)) is False
    assert work_calendar_service._is_work_day(escala, date(2026, 6, 13)) is True


def test_ferias_tem_prioridade_sobre_escala(monkeypatch) -> None:
    escala = criar_escala("12x36", date(2026, 6, 10))
    ferias = SimpleNamespace(id=7, title="Ferias", start_date=date(2026, 6, 10), end_date=date(2026, 6, 10))

    monkeypatch.setattr(work_calendar_service, "obter_work_schedule_ativo_por_usuario", lambda db, user_id: escala)
    monkeypatch.setattr(
        work_calendar_service,
        "listar_vacations_por_usuario_no_intervalo",
        lambda db, user_id, start_date, end_date: [ferias],
    )
    monkeypatch.setattr(
        work_calendar_service,
        "listar_work_calendar_overrides_por_usuario_no_intervalo",
        lambda db, user_id, start_date, end_date: [],
    )

    eventos = work_calendar_service.gerar_eventos_calendario(object(), 1, date(2026, 6, 10), date(2026, 6, 10))

    assert len(eventos) == 1
    assert eventos[0].category == "vacation"
    assert eventos[0].title == "Ferias"


def test_excecao_manual_tem_prioridade_sobre_escala(monkeypatch) -> None:
    escala = criar_escala("12x36", date(2026, 6, 10))
    excecao = SimpleNamespace(
        id=9,
        title="Troca de plantao",
        override_date=date(2026, 6, 10),
        is_working_day=False,
    )

    monkeypatch.setattr(work_calendar_service, "obter_work_schedule_ativo_por_usuario", lambda db, user_id: escala)
    monkeypatch.setattr(
        work_calendar_service,
        "listar_vacations_por_usuario_no_intervalo",
        lambda db, user_id, start_date, end_date: [],
    )
    monkeypatch.setattr(
        work_calendar_service,
        "listar_work_calendar_overrides_por_usuario_no_intervalo",
        lambda db, user_id, start_date, end_date: [excecao],
    )

    eventos = work_calendar_service.gerar_eventos_calendario(object(), 1, date(2026, 6, 10), date(2026, 6, 10))

    assert len(eventos) == 1
    assert eventos[0].category == "exception"
    assert eventos[0].is_working_day is False


def test_evento_de_feriado_nacional_e_incluido(monkeypatch) -> None:
    monkeypatch.setattr(work_calendar_service, "obter_work_schedule_ativo_por_usuario", lambda db, user_id: None)
    monkeypatch.setattr(
        work_calendar_service,
        "listar_vacations_por_usuario_no_intervalo",
        lambda db, user_id, start_date, end_date: [],
    )
    monkeypatch.setattr(
        work_calendar_service,
        "listar_work_calendar_overrides_por_usuario_no_intervalo",
        lambda db, user_id, start_date, end_date: [],
    )

    eventos = work_calendar_service.gerar_eventos_calendario(object(), 1, date(2026, 9, 7), date(2026, 9, 7))

    categorias = {evento.category for evento in eventos}
    assert "holiday" in categorias
