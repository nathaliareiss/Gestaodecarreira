from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import HistoricoFuncional
from backend.repositories.historico_funcional_repository import (
    criar_historico,
    obter_ultimo_historico_por_usuario,
)
from backend.schemas.historico_funcional_schema import (
    AfastamentosUploadRequest,
    HistoricoFuncionalResponse,
    HistoricoFuncionalUploadRequest,
    HistoricoFuncionalResumoGraficoResponse,
)
from backend.services.historico_funcional_service import (
    analisar_historico_funcional,
    analisar_afastamentos_pdf,
    decodificar_arquivo_base64,
)

router = APIRouter(prefix="/historicos-funcionais", tags=["historicos-funcionais"])


def _normalizar_dados_historico_salvo(dados: dict) -> dict:
    if "resumo_grafico" in dados and isinstance(dados["resumo_grafico"], dict):
        return dados

    eventos = dados.get("eventos") or []
    eventos_por_status: dict[str, int] = {}
    eventos_por_tipo: dict[str, int] = {}

    for evento in eventos:
        status = str(evento.get("status", "nao_aplicavel"))
        tipo = str(evento.get("tipo", "substituicao"))
        eventos_por_status[status] = eventos_por_status.get(status, 0) + 1
        eventos_por_tipo[tipo] = eventos_por_tipo.get(tipo, 0) + 1

    dias_trabalhados = int(dados.get("dias_trabalhados") or 0)
    dias_totais = int(dados.get("dias_totais_ate_aposentadoria") or 0)
    percentual_trabalhado = float(dados.get("percentual_trabalhado") or 0)
    percentual_restante = float(dados.get("percentual_restante") or 0)

    dados["resumo_grafico"] = HistoricoFuncionalResumoGraficoResponse(
        tempo_trabalhado_dias=dias_trabalhados,
        tempo_restante_dias=max(dias_totais - dias_trabalhados, 0),
        percentual_trabalhado=percentual_trabalhado,
        percentual_restante=percentual_restante,
        eventos_totais=len(eventos),
        eventos_por_status=eventos_por_status,
        eventos_por_tipo=eventos_por_tipo,
    ).model_dump(mode="json")
    return dados


@router.post("/analisar", response_model=HistoricoFuncionalResponse, status_code=status.HTTP_201_CREATED)
def analisar_e_salvar_historico(
    dados: HistoricoFuncionalUploadRequest,
    db: Session = Depends(get_db),
) -> HistoricoFuncionalResponse:
    try:
        conteudo_pdf = decodificar_arquivo_base64(dados.arquivo_base64)
        conteudo_afastamentos_pdf = (
            decodificar_arquivo_base64(dados.afastamentos_arquivo_base64)
            if dados.afastamentos_arquivo_base64
            else None
        )
        resposta, texto_extraido = analisar_historico_funcional(
            conteudo_pdf=conteudo_pdf,
            arquivo_nome=dados.arquivo_nome,
            usuario_id=dados.usuario_id,
            data_nascimento=dados.data_nascimento,
            anos_clt_averbados=dados.anos_clt_averbados,
            conteudo_afastamentos_pdf=conteudo_afastamentos_pdf,
            arquivo_afastamentos_nome=dados.afastamentos_arquivo_nome,
        )
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel analisar o arquivo enviado. Verifique o PDF e tente novamente.",
        ) from erro

    historico = HistoricoFuncional(
        usuario_id=dados.usuario_id,
        arquivo_nome=resposta.arquivo_nome,
        nome=resposta.nome,
        masp=resposta.masp,
        cpf=resposta.cpf,
        data_emissao=resposta.data_emissao,
        data_nascimento=resposta.data_nascimento,
        data_posse=resposta.data_posse,
        data_exercicio=resposta.data_exercicio,
        cargo_atual=resposta.cargo_atual,
        simbolo_atual=resposta.simbolo_atual,
        nivel_atual=resposta.nivel_atual,
        grau_atual=resposta.grau_atual,
        tempo_clt_averbado_anos=resposta.tempo_clt_averbado_anos,
        tempo_clt_creditado_anos=resposta.tempo_clt_creditado_anos,
        texto_extraido=texto_extraido,
        dados_json="{}",
    )
    historico = criar_historico(db, historico)

    resposta = resposta.model_copy(update={"historico_id": historico.id})
    historico.dados_json = json.dumps(resposta.model_dump(mode="json"), ensure_ascii=False)
    db.add(historico)
    db.commit()
    db.refresh(historico)

    return resposta


@router.post("/usuario/{usuario_id}/afastamentos", response_model=HistoricoFuncionalResponse)
def anexar_afastamentos_historico(
    usuario_id: int,
    dados: AfastamentosUploadRequest,
    db: Session = Depends(get_db),
) -> HistoricoFuncionalResponse:
    historico = obter_ultimo_historico_por_usuario(db, usuario_id)
    if historico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum historico funcional encontrado para este usuario.",
        )

    try:
        dados_historico = json.loads(historico.dados_json)
        dados_historico = _normalizar_dados_historico_salvo(dados_historico)
        conteudo_afastamentos_pdf = decodificar_arquivo_base64(dados.arquivo_base64)
        afastamentos, resumo_afastamentos = analisar_afastamentos_pdf(conteudo_afastamentos_pdf)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel analisar o arquivo de afastamentos. Verifique o PDF e tente novamente.",
        ) from erro

    resposta = HistoricoFuncionalResponse.model_validate(dados_historico).model_copy(
        update={
            "afastamentos_arquivo_nome": dados.arquivo_nome,
            "afastamentos_resumo": resumo_afastamentos,
            "afastamentos": [
                {
                    "tipo": afastamento.tipo,
                    "data_inicio": afastamento.data_inicio,
                    "data_fim": afastamento.data_fim,
                    "total_dias": afastamento.total_dias,
                    "legislacao": afastamento.legislacao,
                    "publicacao": afastamento.publicacao,
                }
                for afastamento in afastamentos
            ],
        }
    )

    historico.dados_json = json.dumps(resposta.model_dump(mode="json"), ensure_ascii=False)
    db.add(historico)
    db.commit()
    db.refresh(historico)

    return resposta


@router.get("/usuario/{usuario_id}/ultimo", response_model=HistoricoFuncionalResponse)
def obter_ultimo_historico_do_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
) -> HistoricoFuncionalResponse:
    historico = obter_ultimo_historico_por_usuario(db, usuario_id)
    if historico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum historico funcional encontrado para este usuario.",
        )

    try:
        dados = json.loads(historico.dados_json)
        dados = _normalizar_dados_historico_salvo(dados)
        return HistoricoFuncionalResponse.model_validate(dados)
    except Exception as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Nao foi possivel carregar o historico funcional salvo.",
        ) from erro
