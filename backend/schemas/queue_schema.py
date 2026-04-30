from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class JobAgendadoResponse(BaseModel):
    job_id: str = Field(min_length=1)
    status: Literal["queued"]
    detail: str | None = None


class JobStatusResponse(BaseModel):
    job_id: str = Field(min_length=1)
    status: Literal["queued", "started", "finished", "failed"]
    result: dict[str, Any] | None = None
    detail: str | None = None
