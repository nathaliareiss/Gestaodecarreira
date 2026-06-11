from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

ScheduleType = Literal["12x36", "24x72", "5x2", "custom"]
VacationType = Literal["regular", "premium"]


class WorkScheduleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    schedule_type: ScheduleType
    anchor_date: date
    state_code: str | None = Field(default=None, max_length=2)
    city_name: str | None = Field(default=None, max_length=120)
    working_weekdays: list[int] = Field(default_factory=list)
    custom_pattern: list[bool] = Field(default_factory=list)
    note: str | None = Field(default=None, max_length=1000)
    is_active: bool = True

    @field_validator("working_weekdays")
    @classmethod
    def validar_working_weekdays(cls, value: list[int]) -> list[int]:
        return [int(item) for item in value if int(item) in {0, 1, 2, 3, 4, 5, 6}]


class WorkScheduleResponse(BaseModel):
    id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    name: str
    schedule_type: ScheduleType
    anchor_date: date
    state_code: str | None = None
    city_name: str | None = None
    working_weekdays: list[int] = Field(default_factory=list)
    custom_pattern: list[bool] = Field(default_factory=list)
    note: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class VacationPeriodCreateRequest(BaseModel):
    title: str = Field(default="Ferias", min_length=1, max_length=120)
    vacation_type: VacationType = "regular"
    start_date: date
    end_date: date | None = None
    requested_days: int | None = Field(default=None, gt=0, le=90)
    note: str | None = Field(default=None, max_length=1000)


class VacationPeriodResponse(BaseModel):
    id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    title: str
    vacation_type: VacationType = "regular"
    start_date: date
    end_date: date
    requested_days: int | None = None
    counted_days: int | None = None
    note: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkCalendarOverrideCreateRequest(BaseModel):
    override_date: date
    is_working_day: bool
    title: str = Field(default="Excecao manual", min_length=1, max_length=120)
    note: str | None = Field(default=None, max_length=1000)


class WorkCalendarOverrideResponse(BaseModel):
    id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    override_date: date
    is_working_day: bool
    title: str
    note: str | None = None
    created_at: datetime
    updated_at: datetime


class WorkCalendarEventResponse(BaseModel):
    id: str
    title: str
    start: date
    end: date
    all_day: bool = True
    category: Literal["work", "off", "vacation", "premium_vacation", "holiday", "exception"]
    color: str
    text_color: str = "#08111d"
    source: str
    is_working_day: bool
