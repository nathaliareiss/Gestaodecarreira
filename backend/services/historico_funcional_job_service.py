from __future__ import annotations

import json

from sqlalchemy.orm import Session

from backend.database.models import HistoricoFuncional
from backend.logger import logger
from backend.cache.redis_cache import (
    CACHE_TTL_HISTORICO_ULTIMO_SEGUNDOS,
    chave_historico_ultimo_usuario,
    definir_json_cache,
)
from backend.repositories.historico_funcional_repository import (
    criar_historico,
    obter_ultimo_historico_por_usuario,
)
from backend.repositories.usuario_repository import atualizar_usuario, obter_usuario_por_id
from backend.schemas.historico_funcional_schema import (
    AfastamentosUploadRequest,
    HistoricoFuncionalResponse,
    HistoricoFuncionalUploadRequest,
    HistoricoFuncionalResumoGraficoResponse,
)
from backend.storage import baixar_pdf_storage
from backend.services.historico_funcional_service import (
    analisar_afastamentos_pdf,
    analisar_historico_funcional,
)


def normalizar_dados_historico_salvo(
    dados: dict,
    historico_id: int,
    usuario_id: int | None,
) -> dict:
    dados["historico_id"] = dados.get("historico_id") or historico_id
    if usuario_id is not None:
        dados["usuario_id"] = dados.get("usuario_id") if dados.get("usuario_id") is not None else usuario_id

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

    if "afastamentos" not in dados or not isinstance(dados.get("afastamentos"), list):
        dados["afastamentos"] = []

    if "eventos" not in dados or not isinstance(dados.get("eventos"), list):
        dados["eventos"] = []

    if "afastamentos_resumo" in dados and dados["afastamentos_resumo"] is not None:
        if not isinstance(dados["afastamentos_resumo"], dict):
            dados["afastamentos_resumo"] = None

    return dados


def _persistir_historico_analisado(
    db: Session,
    resposta: HistoricoFuncionalResponse,
    texto_extraido: str,
    arquivo_nome: str,
    usuario_id: int | None,
    arquivo_storage_path: str,
    afastamentos_storage_path: str | None,
    armazenamento_origem: str,
    processamento_origem: str,
) -> HistoricoFuncionalResponse:
    historico = HistoricoFuncional(
        usuario_id=usuario_id,
        arquivo_nome=resposta.arquivo_nome,
        arquivo_storage_path=arquivo_storage_path,
        afastamentos_storage_path=afastamentos_storage_path,
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

    if usuario_id is not None:
        usuario = obter_usuario_por_id(db, usuario_id)
        if usuario is not None and usuario.data_exercicio is None:
            usuario.data_exercicio = resposta.data_exercicio
            atualizar_usuario(db, usuario)
            logger.info(
                "Data de exercicio atualizada a partir do historico",
                extra={"usuario_id": usuario.id, "historico_id": historico.id},
            )

    resposta = resposta.model_copy(update={"historico_id": historico.id})
    resposta = resposta.model_copy(
        update={
            "armazenamento_origem": armazenamento_origem,
            "processamento_origem": processamento_origem,
        }
    )
    historico.dados_json = json.dumps(resposta.model_dump(mode="json"), ensure_ascii=False)
    db.add(historico)
    db.commit()
    db.refresh(historico)
    if usuario_id is not None:
        definir_json_cache(
            chave_historico_ultimo_usuario(usuario_id),
            resposta.model_dump(mode="json"),
            CACHE_TTL_HISTORICO_ULTIMO_SEGUNDOS,
        )
    logger.info(
        "Historico funcional salvo",
        extra={
            "historico_id": historico.id,
            "user_id": usuario_id,
            "arquivo_nome": arquivo_nome,
        },
    )
    return resposta


def processar_historico_funcional_db(
    db: Session,
    dados: HistoricoFuncionalUploadRequest,
    processamento_origem: str = "direto",
) -> HistoricoFuncionalResponse:
    conteudo_pdf = baixar_pdf_storage(dados.arquivo_storage_path)
    conteudo_afastamentos_pdf = (
        baixar_pdf_storage(dados.afastamentos_storage_path)
        if dados.afastamentos_storage_path
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
    return _persistir_historico_analisado(
        db=db,
        resposta=resposta,
        texto_extraido=texto_extraido,
        arquivo_nome=dados.arquivo_nome,
        usuario_id=dados.usuario_id,
        arquivo_storage_path=dados.arquivo_storage_path,
        afastamentos_storage_path=dados.afastamentos_storage_path,
        armazenamento_origem="local",
        processamento_origem=processamento_origem,
    )


def processar_afastamentos_db(
    db: Session,
    usuario_id: int,
    dados: AfastamentosUploadRequest,
    processamento_origem: str = "direto",
) -> HistoricoFuncionalResponse:
    historico = obter_ultimo_historico_por_usuario(db, usuario_id)
    if historico is None:
        raise ValueError("Nenhum historico funcional encontrado para este usuario.")

    dados_historico = json.loads(historico.dados_json)
    dados_historico = normalizar_dados_historico_salvo(dados_historico, historico.id, usuario_id)
    conteudo_afastamentos_pdf = baixar_pdf_storage(dados.arquivo_storage_path)
    afastamentos, resumo_afastamentos = analisar_afastamentos_pdf(conteudo_afastamentos_pdf)

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
                    "mes_ano_afastamento": afastamento.mes_ano_afastamento,
                    "dias_restantes_ate_pericia": afastamento.dias_restantes_ate_pericia,
                }
                for afastamento in afastamentos
            ],
            "armazenamento_origem": "local",
            "processamento_origem": processamento_origem,
        }
    )

    historico.dados_json = json.dumps(resposta.model_dump(mode="json"), ensure_ascii=False)
    historico.afastamentos_storage_path = dados.arquivo_storage_path
    db.add(historico)
    db.commit()
    db.refresh(historico)
    definir_json_cache(
        chave_historico_ultimo_usuario(usuario_id),
        resposta.model_dump(mode="json"),
        CACHE_TTL_HISTORICO_ULTIMO_SEGUNDOS,
    )
    logger.info(
        "Afastamentos anexados ao historico",
        extra={
            "historico_id": historico.id,
            "user_id": usuario_id,
            "arquivo_nome": dados.arquivo_nome,
        },
    )
    return resposta
