from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import AUTO_SYNC_DB_SCHEMA, CORS_ORIGINS, FRONTEND_BASE_URL
from backend.database import models as database_models  # noqa: F401
from backend.database.database import Base, engine
from backend.database.create_tables import habilitar_rls_tabelas_publicas, sincronizar_usuario_table
from backend.logger import logger
from backend.middleware.error_middleware import registrar_middleware_de_erros
from backend.middleware.metrics_middleware import registrar_middleware_de_metricas
from backend.routes import router as api_router


def criar_app() -> FastAPI:
    app = FastAPI(
        title="Gestao de Carreira API",
        version="0.1.0",
    )

    origens_cors = CORS_ORIGINS or ([FRONTEND_BASE_URL] if FRONTEND_BASE_URL else ["*"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origens_cors,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    registrar_middleware_de_erros(app)
    registrar_middleware_de_metricas(app)
    app.include_router(api_router)

    @app.get("/")
    def raiz() -> dict[str, str]:
        return {"status": "ok", "service": "Gestao de Carreira API"}

    @app.on_event("startup")
    def _criar_tabelas() -> None:
        Base.metadata.create_all(bind=engine)
        habilitar_rls_tabelas_publicas()
        if AUTO_SYNC_DB_SCHEMA:
            sincronizar_usuario_table()
        logger.info(
            "Aplicacao FastAPI iniciada com sucesso",
            extra={
                "titulo": "Gestao de Carreira API",
                "origens_cors": origens_cors,
                "auto_sync_db_schema": AUTO_SYNC_DB_SCHEMA,
            },
        )

    return app


app = criar_app()
