from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.models.servidora import Servidora
from backend.schemas.carreira_api_schema import (
    CadastroCarreiraRequest,
    ResumoCarreiraResponse,
)
from backend.services.carreira_service import montar_resumo_funcional

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

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/carreira/resumo", response_model=ResumoCarreiraResponse)
    def criar_resumo(cadastro: CadastroCarreiraRequest) -> ResumoCarreiraResponse:
        servidora = Servidora(
            nome=cadastro.nome,
            data_nascimento=cadastro.data_nascimento,
            data_ingresso=cadastro.data_ingresso,
            tem_tempo_clt_averbado=cadastro.tem_tempo_clt_averbado,
        )

        resumo = montar_resumo_funcional(servidora)
        payload = {
            **asdict(resumo),
            "nome": servidora.nome,
            "data_nascimento": servidora.data_nascimento,
            "data_ingresso": servidora.data_ingresso,
            "tem_tempo_clt_averbado": servidora.tem_tempo_clt_averbado,
        }
        return ResumoCarreiraResponse(**payload)

    return app


app = criar_app()
