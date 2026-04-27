from __future__ import annotations

import os
from dataclasses import asdict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.models.servidora import Servidora
from backend.schemas.carreira_api_schema import (
    CadastroCarreiraRequest,
    ResumoCarreiraResponse,
)
from backend.services.carreira_service import montar_resumo_funcional


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


def run() -> None:
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("UVICORN_RELOAD", "true").lower() in {"1", "true", "yes", "sim"}
    uvicorn.run("backend.api:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run()
