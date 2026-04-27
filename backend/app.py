from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import router as api_router

load_dotenv(Path(__file__).resolve().parent / ".env")


def _ler_origens_cors() -> list[str]:
    origens = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    return [origem.strip() for origem in origens.split(",") if origem.strip()]


def criar_app() -> FastAPI:
    app = FastAPI(
        title="Gestao de Carreira API",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_ler_origens_cors(),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


app = criar_app()
