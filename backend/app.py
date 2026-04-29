from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import CORS_ORIGINS
from backend.database.create_tables import sincronizar_usuario_table
from backend.middleware.error_middleware import registrar_middleware_de_erros
from backend.routes import router as api_router


def criar_app() -> FastAPI:
    app = FastAPI(
        title="Gestao de Carreira API",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    registrar_middleware_de_erros(app)
    app.include_router(api_router)

    @app.on_event("startup")
    def _criar_tabelas() -> None:
        sincronizar_usuario_table()

    return app


app = criar_app()
