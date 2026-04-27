from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter

from backend.models.servidora import Servidora
from backend.schemas.carreira_api_schema import (
    CadastroCarreiraRequest,
    ResumoCarreiraResponse,
)
from backend.services.carreira_service import montar_resumo_funcional

router = APIRouter(prefix="/carreira", tags=["carreira"])


@router.post("/resumo", response_model=ResumoCarreiraResponse)
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
