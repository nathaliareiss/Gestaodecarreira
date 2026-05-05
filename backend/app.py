from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import AUTO_SYNC_DB_SCHEMA
from backend.logger import logger
from backend.database.create_tables import sincronizar_usuario_table
from backend.middleware.error_middleware import registrar_middleware_de_erros
from backend.middleware.metrics_middleware import registrar_middleware_de_metricas
from backend.routes import router as api_router


def criar_app() -> FastAPI:
    app = FastAPI(
        title="Gestao de Carreira API",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    registrar_middleware_de_erros(app)
    registrar_middleware_de_metricas(app)
    app.include_router(api_router)

    @app.on_event("startup")
    def _criar_tabelas() -> None:
        if AUTO_SYNC_DB_SCHEMA:
            sincronizar_usuario_table()
        logger.info(
            "Aplicacao FastAPI iniciada com sucesso",
            extra={
                "titulo": "Gestao de Carreira API",
                "origens_cors": ["*"],
                "auto_sync_db_schema": AUTO_SYNC_DB_SCHEMA,
            },
        )

    return app


app = criar_app()
