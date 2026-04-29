from __future__ import annotations

import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

logger = logging.getLogger(__name__)


def registrar_middleware_de_erros(app) -> None:
    @app.middleware("http")
    async def capturar_erros_internos(request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            raise
        except Exception:
            logger.exception(
                "Erro interno nao tratado em %s %s",
                request.method,
                request.url.path,
            )
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": (
                        "Nao foi possivel concluir esta operacao. "
                        "Tente novamente em alguns instantes."
                    )
                },
            )
