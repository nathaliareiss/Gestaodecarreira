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
    HistoricoFuncionalResponse,
    HistoricoFuncionalUploadRequest,
)
from backend.services.historico_funcional_service import (
    analisar_historico_funcional,
    decodificar_arquivo_base64,
)

router = APIRouter(prefix="/historicos-funcionais", tags=["historicos-funcionais"])


@router.post("/analisar", response_model=HistoricoFuncionalResponse, status_code=status.HTTP_201_CREATED)
def analisar_e_salvar_historico(
    dados: HistoricoFuncionalUploadRequest,
    db: Session = Depends(get_db),
) -> HistoricoFuncionalResponse:
    try:
        conteudo_pdf = decodificar_arquivo_base64(dados.arquivo_base64)
        resposta, texto_extraido = analisar_historico_funcional(
            conteudo_pdf=conteudo_pdf,
            arquivo_nome=dados.arquivo_nome,
            usuario_id=dados.usuario_id,
            data_nascimento=dados.data_nascimento,
            anos_clt_averbados=dados.anos_clt_averbados,
        )
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(erro)) from erro

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
        return HistoricoFuncionalResponse.model_validate(dados)
    except Exception as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Nao foi possivel carregar o historico funcional salvo.",
        ) from erro
