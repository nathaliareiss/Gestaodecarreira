from __future__ import annotations

import json
from datetime import date

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
    FeriasUploadRequest,
    HistoricoFuncionalResponse,
    HistoricoFuncionalUploadRequest,
    HistoricoFuncionalResumoGraficoResponse,
)
from backend.schemas.work_calendar_schema import VacationPeriodCreateRequest
from backend.storage import baixar_pdf_storage
from backend.services.historico_funcional_service import (
    AfastamentoPeriodo,
    EventoHistorico,
    _cronometro_ate_aposentadoria,
    _categoria_previdenciaria_por_cargo,
    _fim_estagio_probatorio,
    analisar_afastamentos_pdf,
    analisar_ferias_pdf,
    analisar_historico_funcional,
    montar_resumo_aposentadoria,
)
from backend.services.work_calendar_service import criar_periodo_ferias, listar_periodos_ferias


def _sincronizar_ferias_no_calendario(db: Session, usuario_id: int | None, resposta: HistoricoFuncionalResponse) -> None:
    if usuario_id is None or not resposta.ferias:
        return

    existentes = {
        (item.vacation_type, item.start_date, item.end_date)
        for item in listar_periodos_ferias(db, usuario_id)
    }
    for periodo in resposta.ferias:
        chave = (periodo.tipo, periodo.data_inicio, periodo.data_fim)
        if chave in existentes:
            continue
        criar_periodo_ferias(
            db,
            usuario_id,
            VacationPeriodCreateRequest(
                title="Ferias premio" if periodo.tipo == "premium" else "Ferias regulamentares",
                vacation_type=periodo.tipo,
                start_date=periodo.data_inicio,
                end_date=periodo.data_fim,
                requested_days=periodo.dias_contabilizados,
                note="Importado automaticamente do PDF de ferias.",
            ),
        )
        existentes.add(chave)


def _eventos_salvos_para_modelo(eventos: list[dict]) -> list[EventoHistorico]:
    convertidos: list[EventoHistorico] = []
    for evento in eventos:
        try:
            convertidos.append(
                EventoHistorico(
                    tipo=evento.get("tipo", "substituicao"),
                    descricao=str(evento.get("descricao") or ""),
                    cargo=str(evento.get("cargo") or ""),
                    simbolo=str(evento.get("simbolo") or ""),
                    nivel=str(evento.get("nivel") or ""),
                    grau=str(evento.get("grau") or ""),
                    data_publicacao=date.fromisoformat(str(evento["data_publicacao"])),
                    data_efetiva=date.fromisoformat(str(evento["data_efetiva"])),
                    data_prevista=(
                        date.fromisoformat(str(evento["data_prevista"]))
                        if evento.get("data_prevista")
                        else None
                    ),
                    status=evento.get("status", "nao_aplicavel"),
                    atraso_dias=int(evento.get("atraso_dias") or 0),
                )
            )
        except Exception:
            continue
    return convertidos


def _afastamentos_salvos_para_modelo(afastamentos: list[dict]) -> list[AfastamentoPeriodo]:
    convertidos: list[AfastamentoPeriodo] = []
    for afastamento in afastamentos:
        try:
            convertidos.append(
                AfastamentoPeriodo(
                    tipo=afastamento.get("tipo", "licenca_para_tratamento_de_saude"),
                    data_inicio=date.fromisoformat(str(afastamento["data_inicio"])),
                    data_fim=date.fromisoformat(str(afastamento["data_fim"])),
                    total_dias=int(afastamento.get("total_dias") or 0),
                    legislacao=afastamento.get("legislacao"),
                    publicacao=(
                        date.fromisoformat(str(afastamento["publicacao"]))
                        if afastamento.get("publicacao")
                        else None
                    ),
                    mes_ano_afastamento=str(afastamento.get("mes_ano_afastamento") or ""),
                    dias_restantes_ate_pericia=int(afastamento.get("dias_restantes_ate_pericia") or 0),
                )
            )
        except Exception:
            continue
    return convertidos


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

    try:
        data_nascimento = date.fromisoformat(str(dados["data_nascimento"]))
        data_exercicio = date.fromisoformat(str(dados["data_exercicio"]))
        anos_clt_averbados = int(dados.get("tempo_clt_averbado_anos") or 0)
        sexo = dados.get("sexo") if dados.get("sexo") in {"feminino", "masculino"} else "feminino"
        categoria = dados.get("categoria_previdenciaria") or "geral"
        texto_cargo = " ".join(
            str(valor or "")
            for valor in (
                dados.get("cargo_atual"),
                dados.get("simbolo_atual"),
                *[evento.get("cargo") for evento in eventos if isinstance(evento, dict)],
                *[evento.get("descricao") for evento in eventos if isinstance(evento, dict)],
            )
        )
        categoria = _categoria_previdenciaria_por_cargo(categoria, texto_cargo)
        dados["categoria_previdenciaria"] = categoria
        (
            dados["data_aposentadoria_por_carreira"],
            dados["data_aposentadoria_por_idade"],
            dados["data_aposentadoria_prevista"],
            dias_trabalhados,
            dias_totais,
            percentual_trabalhado,
            percentual_restante,
        ) = _cronometro_ate_aposentadoria(
            data_nascimento=data_nascimento,
            data_exercicio=data_exercicio,
            anos_clt_averbados=anos_clt_averbados,
            sexo=sexo,
            categoria_previdenciaria=categoria,
        )
        dados["dias_trabalhados"] = dias_trabalhados
        dados["dias_totais_ate_aposentadoria"] = dias_totais
        dados["percentual_trabalhado"] = percentual_trabalhado
        dados["percentual_restante"] = percentual_restante
        eventos_modelo = _eventos_salvos_para_modelo(eventos if isinstance(eventos, list) else [])
        afastamentos_modelo = _afastamentos_salvos_para_modelo(
            dados.get("afastamentos") if isinstance(dados.get("afastamentos"), list) else []
        )
        dados["resumo_aposentadoria"] = montar_resumo_aposentadoria(
            data_nascimento=data_nascimento,
            data_aposentadoria_por_carreira=dados["data_aposentadoria_por_carreira"],
            data_aposentadoria_por_idade=dados["data_aposentadoria_por_idade"],
            data_aposentadoria_prevista=dados["data_aposentadoria_prevista"],
            eventos=eventos_modelo,
            simbolo_atual=str(dados.get("simbolo_atual") or ""),
            nivel_atual=str(dados.get("nivel_atual") or ""),
            grau_atual=str(dados.get("grau_atual") or ""),
            inicio_contagem_progressao=_fim_estagio_probatorio(data_exercicio),
            afastamentos=afastamentos_modelo,
        ).model_dump(mode="json")
    except Exception:
        logger.warning(
            "Nao foi possivel recalcular aposentadoria do historico salvo",
            extra={"historico_id": historico_id, "user_id": usuario_id},
        )

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

    if "ferias" not in dados or not isinstance(dados.get("ferias"), list):
        dados["ferias"] = []

    if "ferias_resumo" in dados and dados["ferias_resumo"] is not None:
        if not isinstance(dados["ferias_resumo"], dict):
            dados["ferias_resumo"] = None

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
    ferias_storage_path: str | None,
    armazenamento_origem: str,
    processamento_origem: str,
) -> HistoricoFuncionalResponse:
    historico = HistoricoFuncional(
        usuario_id=usuario_id,
        arquivo_nome=resposta.arquivo_nome,
        arquivo_storage_path=arquivo_storage_path,
        afastamentos_storage_path=afastamentos_storage_path,
        ferias_storage_path=ferias_storage_path,
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
    conteudo_ferias_pdf = (
        baixar_pdf_storage(dados.ferias_storage_path)
        if dados.ferias_storage_path
        else None
    )
    resposta, texto_extraido = analisar_historico_funcional(
        conteudo_pdf=conteudo_pdf,
        arquivo_nome=dados.arquivo_nome,
        usuario_id=dados.usuario_id,
        data_nascimento=dados.data_nascimento,
        sexo=dados.sexo,
        categoria_previdenciaria=dados.categoria_previdenciaria,
        anos_clt_averbados=dados.anos_clt_averbados,
        conteudo_afastamentos_pdf=conteudo_afastamentos_pdf,
        arquivo_afastamentos_nome=dados.afastamentos_arquivo_nome,
        conteudo_ferias_pdf=conteudo_ferias_pdf,
        arquivo_ferias_nome=dados.ferias_arquivo_nome,
    )
    resposta = _persistir_historico_analisado(
        db=db,
        resposta=resposta,
        texto_extraido=texto_extraido,
        arquivo_nome=dados.arquivo_nome,
        usuario_id=dados.usuario_id,
        arquivo_storage_path=dados.arquivo_storage_path,
        afastamentos_storage_path=dados.afastamentos_storage_path,
        ferias_storage_path=dados.ferias_storage_path,
        armazenamento_origem="local",
        processamento_origem=processamento_origem,
    )
    _sincronizar_ferias_no_calendario(db, dados.usuario_id, resposta)
    return resposta


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


def processar_ferias_db(
    db: Session,
    usuario_id: int,
    dados: FeriasUploadRequest,
    processamento_origem: str = "direto",
) -> HistoricoFuncionalResponse:
    historico = obter_ultimo_historico_por_usuario(db, usuario_id)
    if historico is None:
        raise ValueError("Nenhum historico funcional encontrado para este usuario.")

    dados_historico = json.loads(historico.dados_json)
    dados_historico = normalizar_dados_historico_salvo(dados_historico, historico.id, usuario_id)
    conteudo_ferias_pdf = baixar_pdf_storage(dados.arquivo_storage_path)
    ferias, resumo_ferias = analisar_ferias_pdf(conteudo_ferias_pdf)

    resposta = HistoricoFuncionalResponse.model_validate(dados_historico).model_copy(
        update={
            "ferias_arquivo_nome": dados.arquivo_nome,
            "ferias_resumo": resumo_ferias,
            "ferias": [
                {
                    "tipo": item.tipo,
                    "data_inicio": item.data_inicio,
                    "data_fim": item.data_fim,
                    "dias_contabilizados": item.dias_contabilizados,
                    "dias_corridos": item.dias_corridos,
                    "regra_contagem": item.regra_contagem,
                    "observacao": item.observacao,
                }
                for item in ferias
            ],
            "armazenamento_origem": "local",
            "processamento_origem": processamento_origem,
        }
    )

    historico.dados_json = json.dumps(resposta.model_dump(mode="json"), ensure_ascii=False)
    historico.ferias_storage_path = dados.arquivo_storage_path
    db.add(historico)
    db.commit()
    db.refresh(historico)
    _sincronizar_ferias_no_calendario(db, usuario_id, resposta)
    definir_json_cache(
        chave_historico_ultimo_usuario(usuario_id),
        resposta.model_dump(mode="json"),
        CACHE_TTL_HISTORICO_ULTIMO_SEGUNDOS,
    )
    logger.info(
        "Ferias anexadas ao historico",
        extra={
            "historico_id": historico.id,
            "user_id": usuario_id,
            "arquivo_nome": dados.arquivo_nome,
        },
    )
    return resposta
