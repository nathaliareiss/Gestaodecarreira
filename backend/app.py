from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.config import (
    AUTO_SYNC_DB_SCHEMA,
    CORS_ORIGINS,
    FRONTEND_BASE_URL,
    SECRET_KEY,
    SMTP_FROM,
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_USER,
)
from backend.database import models as database_models  # noqa: F401
from backend.database.database import Base, engine
from backend.database.create_tables import habilitar_rls_tabelas_publicas, sincronizar_usuario_table
from backend.logger import logger
from backend.middleware.error_middleware import registrar_middleware_de_erros
from backend.middleware.metrics_middleware import registrar_middleware_de_metricas
from backend.routes import router as api_router


def _resumir_database_url(url: str) -> dict[str, str | int | None]:
    if not url:
        return {"definida": False}

    partes = urlparse(url)
    return {
        "definida": True,
        "scheme": partes.scheme,
        "host": partes.hostname,
        "porta": partes.port,
        "banco": partes.path.lstrip("/") or None,
    }


def _validar_configuracao_autenticacao_email() -> None:
    faltando: list[str] = []

    if not os.getenv("DATABASE_URL", "").strip():
        faltando.append("DATABASE_URL")

    if not FRONTEND_BASE_URL:
        faltando.append("FRONTEND_BASE_URL")

    if not CORS_ORIGINS:
        faltando.append("CORS_ORIGINS")

    if not SMTP_HOST:
        faltando.append("SMTP_HOST")

    if not os.getenv("SMTP_PORT", "").strip():
        faltando.append("SMTP_PORT")

    if not SMTP_USER:
        faltando.append("SMTP_USER")

    if not os.getenv("SMTP_PASSWORD", "").strip():
        faltando.append("SMTP_PASSWORD")

    if not (SMTP_FROM or SMTP_FROM_EMAIL):
        faltando.append("SMTP_FROM")

    if not SECRET_KEY:
        faltando.append("SECRET_KEY")

    logger.info(
        "Configuracao de autenticacao e email avaliada",
        extra={
            "campos_faltantes": faltando,
            "database": _resumir_database_url(os.getenv("DATABASE_URL", "")),
        },
    )

    if faltando:
        logger.warning(
            "Configuracao de autenticacao e email incompleta",
            extra={"campos_faltantes": faltando},
        )


def criar_app() -> FastAPI:
    app = FastAPI(
        title="Gestao de Carreira API",
        version="0.1.0",
    )
    downloads_dir = Path(__file__).resolve().parent / "static" / "downloads"
    installer_filename = "GestaoDeCarreira-Setup-latest.exe"
    installer_path = downloads_dir / installer_filename
    installer_legacy_path = downloads_dir / "GestaoDeCarreira-Setup-1.0.4.exe"

    origens_cors = [
        origem
        for origem in (CORS_ORIGINS or ([FRONTEND_BASE_URL] if FRONTEND_BASE_URL else ["http://localhost:3000"]))
        if origem and origem != "*"
    ]
    if not origens_cors:
        origens_cors = [FRONTEND_BASE_URL] if FRONTEND_BASE_URL else ["http://localhost:3000"]

    @app.get("/downloads/GestaoDeCarreira-Setup-1.0.4.exe")
    def baixar_instalador_legado_104() -> RedirectResponse:
        return RedirectResponse(url="/downloads/GestaoDeCarreira-Setup-latest.exe", status_code=307)

    @app.get("/downloads/GestaoDeCarreira-Setup-1.0.5.exe")
    def baixar_instalador_legado_105() -> RedirectResponse:
        return RedirectResponse(url="/downloads/GestaoDeCarreira-Setup-latest.exe", status_code=307)

    @app.get("/downloads/GestaoDeCarreira-Setup-1.0.6.exe")
    def baixar_instalador_legado_106() -> RedirectResponse:
        return RedirectResponse(url="/downloads/GestaoDeCarreira-Setup-latest.exe", status_code=307)

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

        logger.info(
            "Downloads do assistente verificados no startup",
            extra={
                "downloads_dir": str(downloads_dir),
                "installer_path": str(installer_path),
                "installer_legacy_path": str(installer_legacy_path),
                "installer_exists": installer_path.is_file(),
                "installer_legacy_exists": installer_legacy_path.is_file(),
            },
        )

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
        _validar_configuracao_autenticacao_email()

    return app


app = criar_app()
