from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from backend.metrics import render_metrics

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/metrics", include_in_schema=False)
def metrics() -> PlainTextResponse:
    return PlainTextResponse(render_metrics(), media_type="text/plain; version=0.0.4")
