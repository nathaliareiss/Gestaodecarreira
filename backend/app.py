from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles

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
    downloads_dir = Path(__file__).resolve().parent / "static" / "downloads"

    origens_cors = [
        origem
        for origem in (CORS_ORIGINS or ([FRONTEND_BASE_URL] if FRONTEND_BASE_URL else ["http://localhost:3000"]))
        if origem and origem != "*"
    ]
    if not origens_cors:
        origens_cors = [FRONTEND_BASE_URL] if FRONTEND_BASE_URL else ["http://localhost:3000"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origens_cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    registrar_middleware_de_erros(app)
    registrar_middleware_de_metricas(app)
    app.mount("/downloads", StaticFiles(directory=str(downloads_dir), check_dir=False), name="downloads")
    app.include_router(api_router)

    @app.get("/")
    def raiz() -> dict[str, str]:
        return {"status": "ok", "service": "Gestao de Carreira API"}

    @app.on_event("startup")
    def _criar_tabelas() -> None:
        Base.metadata.create_all(bind=engine)
        habilitar_rls_tabelas_publicas()
        if engine.dialect.name != "sqlite":
            sincronizar_usuario_table()

        rotas_registradas = [
            route.path
            for route in app.routes
            if isinstance(route, APIRoute)
        ]
        for rota in rotas_registradas:
            print(rota)

        rotas_financeiro = [
            route.path
            for route in app.routes
            if isinstance(route, APIRoute) and route.path.startswith("/api/financeiro")
        ]
        logger.info(
            "Aplicacao FastAPI iniciada com sucesso",
            extra={
                "titulo": "Gestao de Carreira API",
                "origens_cors": origens_cors,
                "auto_sync_db_schema": AUTO_SYNC_DB_SCHEMA,
                "schema_sync_executado": engine.dialect.name != "sqlite",
                "rotas_registradas": rotas_registradas,
                "rotas_financeiro": rotas_financeiro,
                "rota_evolucao_salarial": next(
                    (rota for rota in rotas_financeiro if rota.endswith("/evolucao-salarial")),
                    None,
                ),
            },
        )

    return app


app = criar_app()
