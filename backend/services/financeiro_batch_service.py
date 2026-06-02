from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from time import perf_counter
from statistics import median

from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.database.models import Paycheck, PaycheckItem, PayrollBatch
from backend.logger import logger
from backend.metrics import registrar_job_execucao
from backend.repositories.financeiro_repository import (
    atualizar_lote_financeiro,
    existe_paycheck_por_chave_negocio,
    existe_paycheck_por_file_hash,
    obter_lote_financeiro_por_id,
    obter_paychecks_por_batch_id,
    obter_paychecks_por_usuario_id,
    salvar_paycheck_com_itens,
)
from backend.schemas.financeiro_schema import ArquivoFinanceiroJobPayload, LoteFinanceiroJobPayload
from backend.services.contracheque_parser import (
    CATEGORIAS_DESCONTO,
    CATEGORIAS_VANTAGEM,
    extrair_rubricas_contracheque,
    parse_contracheque,
)

ZERO = Decimal("0.00")
THRESHOLD_CRESCIMENTO_RELEVANTE = Decimal("1.00")


def detectar_competencias_faltantes_por_paychecks(paychecks: list[Paycheck]) -> list[str]:
    competencias_unicas = sorted(
        {
            (int(paycheck.ano), int(paycheck.mes))
            for paycheck in paychecks
            if int(getattr(paycheck, "ano", 0) or 0) > 0 and 1 <= int(getattr(paycheck, "mes", 0) or 0) <= 12
        }
    )

    if len(competencias_unicas) < 2:
        return []

    faltantes: list[str] = []

    def proximo_mes(ano: int, mes: int) -> tuple[int, int]:
        if mes >= 12:
            return ano + 1, 1
        return ano, mes + 1

    anterior_ano, anterior_mes = competencias_unicas[0]
    for ano_atual, mes_atual in competencias_unicas[1:]:
        cursor_ano, cursor_mes = proximo_mes(anterior_ano, anterior_mes)
        while (cursor_ano, cursor_mes) != (ano_atual, mes_atual):
            faltantes.append(f"{cursor_mes:02d}/{cursor_ano}")
            cursor_ano, cursor_mes = proximo_mes(cursor_ano, cursor_mes)
        anterior_ano, anterior_mes = ano_atual, mes_atual

    return faltantes


def _para_decimal(valor: object) -> Decimal:
    if isinstance(valor, Decimal):
        return valor

    if valor is None or valor == "":
        return ZERO

    return Decimal(str(valor))


def _criar_paycheck_item(payload: dict[str, object]) -> PaycheckItem:
    return PaycheckItem(
        tipo=str(payload["tipo"]),
        categoria_normalizada=str(payload["categoria_normalizada"]),
        descricao_original=str(payload["descricao_original"]),
        descricao=str(payload["descricao"]),
        valor=_para_decimal(payload["valor"]),
    )


def _hash_sha256_conteudo(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def _ler_mensagens_erro_lote(valor_bruto: str | None) -> list[str]:
    if not valor_bruto:
        return []

    try:
        mensagens = json.loads(valor_bruto)
    except Exception:
        return []

    if not isinstance(mensagens, list):
        return []

    return [str(mensagem).strip() for mensagem in mensagens if str(mensagem).strip()]


def _normalizar_mensagem_erro_processamento(erro: Exception, arquivo_nome: str) -> str:
    mensagem = str(erro).strip()
    mensagem_normalizada = mensagem.lower()
    nome_erro = erro.__class__.__name__.lower()

    if isinstance(erro, ValueError):
        if "competencia" in mensagem_normalizada:
            return "Não foi possível identificar a competência do contracheque."
        if "ja existe" in mensagem_normalizada or "já existe" in mensagem_normalizada:
            return "Já existe um contracheque salvo para esta competência."
        if "lote financeiro nao encontrado" in mensagem_normalizada:
            return "O lote financeiro não foi encontrado."
        return mensagem or f"Falha ao processar o arquivo {arquivo_nome}."

    if "pdf" in mensagem_normalizada or "pdf" in nome_erro:
        return f"O arquivo {arquivo_nome} parece estar inválido ou corrompido."

    if mensagem:
        return f"Falha ao processar o arquivo {arquivo_nome}: {mensagem}"

    return f"Falha ao processar o arquivo {arquivo_nome}."


def _registrar_erro_lote(db: Session, lote: PayrollBatch, mensagem_erro: str) -> None:
    mensagens = _ler_mensagens_erro_lote(getattr(lote, "failure_messages", None))
    if mensagem_erro not in mensagens:
        mensagens.append(mensagem_erro)

    lote.last_error_message = mensagem_erro
    lote.failure_messages = json.dumps(mensagens[-5:], ensure_ascii=False)
    db.add(lote)
    db.commit()
    db.refresh(lote)


def _registrar_metricas_finais_lote(lote: PayrollBatch) -> None:
    total_tratados = lote.processed_files + lote.duplicated_files + lote.failed_files
    if total_tratados <= 0:
        return

    created_at = lote.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    duracao_total_lote_segundos = max(
        (datetime.now(timezone.utc) - created_at).total_seconds(),
        0.0,
    )
    tempo_total_processamento = _para_decimal(getattr(lote, "processing_seconds_total", ZERO))
    tempo_medio_por_pdf_segundos = (
        (tempo_total_processamento / Decimal(total_tratados)).quantize(
            Decimal("0.001"),
            rounding=ROUND_HALF_UP,
        )
        if total_tratados > 0
        else ZERO
    )
    pdfs_por_minuto = (
        (Decimal(total_tratados) / Decimal(max(duracao_total_lote_segundos, 0.001)) * Decimal("60")).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        if duracao_total_lote_segundos > 0
        else ZERO
    )

    logger.info(
        "Lote financeiro finalizado",
        extra={
            "batch_id": lote.id,
            "total_pdfs": lote.total_files,
            "total_tratados": total_tratados,
            "total_processados": lote.processed_files,
            "total_duplicados": lote.duplicated_files,
            "total_falhas": lote.failed_files,
            "tempo_total_lote_segundos": round(duracao_total_lote_segundos, 3),
            "tempo_total_processamento_segundos": float(tempo_total_processamento),
            "tempo_medio_por_pdf_segundos": float(tempo_medio_por_pdf_segundos),
            "pdfs_por_minuto": float(pdfs_por_minuto),
        },
    )


def _processar_arquivo_e_atualizar_lote(
    db: Session,
    *,
    batch_id: int,
    user_id: int | None,
    arquivo_nome: str,
    caminho_temporario: str,
    arquivo_hash: str | None = None,
) -> tuple[str, PayrollBatch, float]:
    inicio = perf_counter()
    lote = obter_lote_financeiro_por_id(db, batch_id)
    if lote is None:
        raise ValueError("Lote financeiro nao encontrado.")

    resultado = _processar_arquivo_individual(
        db=db,
        batch_id=batch_id,
        user_id=user_id,
        arquivo_nome=arquivo_nome,
        caminho_temporario=caminho_temporario,
        arquivo_hash=arquivo_hash,
    )
    duracao_segundos = perf_counter() - inicio

    if resultado == "duplicated":
        lote_atualizado = atualizar_lote_financeiro(
            db,
            lote,
            duplicated_delta=1,
            processing_seconds_delta=duracao_segundos,
        )
    elif resultado == "processed":
        lote_atualizado = atualizar_lote_financeiro(
            db,
            lote,
            processed_delta=1,
            processing_seconds_delta=duracao_segundos,
        )
    else:
        lote_atualizado = atualizar_lote_financeiro(
            db,
            lote,
            failed_delta=1,
            processing_seconds_delta=duracao_segundos,
        )

    total_tratados = (
        lote_atualizado.processed_files
        + lote_atualizado.duplicated_files
        + lote_atualizado.failed_files
    )
    if lote_atualizado.total_files > 0 and total_tratados >= lote_atualizado.total_files:
        _registrar_metricas_finais_lote(lote_atualizado)

    return resultado, lote_atualizado, duracao_segundos


def _criar_paycheck_model(
    batch_id: int,
    user_id: int | None,
    dados: dict[str, object],
    *,
    file_hash: str,
) -> Paycheck:
    competencia = str(dados.get("competencia") or "").strip()
    ano = int(dados.get("ano") or 0)
    mes = int(dados.get("mes") or 0)
    matricula = str(dados.get("matricula") or "").strip()

    if not competencia or ano <= 0 or mes <= 0:
        raise ValueError("Nao foi possivel identificar a competencia do contracheque.")

    return Paycheck(
        batch_id=batch_id,
        user_id=user_id,
        file_hash=file_hash,
        matricula=matricula,
        competencia=competencia,
        ano=ano,
        mes=mes,
        bruto=_para_decimal(dados.get("bruto")),
        descontos=_para_decimal(dados.get("descontos")),
        liquido=_para_decimal(dados.get("liquido")),
        vencimento_basico=_para_decimal(dados.get("vencimento_basico")),
        adicional_desempenho=_para_decimal(dados.get("adicional_desempenho")),
        adicional_noturno=_para_decimal(dados.get("adicional_noturno")),
        irrf=_para_decimal(dados.get("irrf")),
        previdencia=_para_decimal(dados.get("previdencia")),
    )


def _processar_arquivo_individual(
    db: Session,
    batch_id: int,
    user_id: int | None,
    arquivo_nome: str,
    caminho_temporario: str,
    arquivo_hash: str | None = None,
) -> str:
    file_hash = arquivo_hash or _hash_sha256_conteudo(Path(caminho_temporario).read_bytes())

    if existe_paycheck_por_file_hash(db, user_id, file_hash):
        logger.info(
            "Contracheque financeiro duplicado ignorado por hash",
            extra={
                "batch_id": batch_id,
                "arquivo_nome": arquivo_nome,
                "etapa": "duplicado",
                "file_hash": file_hash,
            },
        )
        return "duplicated"

    dados = parse_contracheque(caminho_temporario)
    rubricas = extrair_rubricas_contracheque(caminho_temporario)
    paycheck = _criar_paycheck_model(batch_id, user_id, dados, file_hash=file_hash)

    if existe_paycheck_por_chave_negocio(
        db,
        user_id,
        paycheck.ano,
        paycheck.mes,
        paycheck.matricula,
    ):
        logger.info(
            "Contracheque financeiro duplicado ignorado por competencia",
            extra={
                "batch_id": batch_id,
                "arquivo_nome": arquivo_nome,
                "etapa": "duplicado",
                "competencia": paycheck.competencia,
                "matricula": paycheck.matricula or None,
            },
        )
        return "duplicated"

    itens = [_criar_paycheck_item(item) for item in rubricas]
    salvar_paycheck_com_itens(db, paycheck, itens)
    logger.info(
        "Contracheque financeiro salvo",
        extra={
            "batch_id": batch_id,
            "arquivo_nome": arquivo_nome,
            "competencia": paycheck.competencia,
            "file_hash": file_hash,
            "matricula": paycheck.matricula or None,
        },
    )
    return "processed"


def _processar_arquivo_financeiro_job_em_db(
    db: Session,
    *,
    batch_id: int,
    user_id: int | None,
    arquivo_nome: str,
    caminho_temporario: str,
    arquivo_hash: str | None = None,
) -> dict[str, object]:
    logger.info(
        "Processando arquivo do lote financeiro",
        extra={
            "batch_id": batch_id,
            "arquivo_nome": arquivo_nome,
            "etapa": "processar_arquivo",
        },
    )

    inicio = perf_counter()
    try:
        resultado_arquivo, lote_atualizado, duracao_segundos = _processar_arquivo_e_atualizar_lote(
            db,
            batch_id=batch_id,
            user_id=user_id,
            arquivo_nome=arquivo_nome,
            caminho_temporario=caminho_temporario,
            arquivo_hash=arquivo_hash,
        )
    except Exception as erro_arquivo:
        db.rollback()
        mensagem_erro = _normalizar_mensagem_erro_processamento(erro_arquivo, arquivo_nome)
        logger.exception(
            "Falha ao processar contracheque do lote",
            extra={
                "batch_id": batch_id,
                "arquivo_nome": arquivo_nome,
                "etapa": "processar_arquivo",
                "erro": str(erro_arquivo),
                "mensagem_erro": mensagem_erro,
            },
        )
        lote_atual = obter_lote_financeiro_por_id(db, batch_id)
        if lote_atual is None:
            raise ValueError("Lote financeiro nao encontrado.") from erro_arquivo

        _registrar_erro_lote(db, lote_atual, mensagem_erro)
        lote_atualizado = atualizar_lote_financeiro(
            db,
            lote_atual,
            failed_delta=1,
            processing_seconds_delta=perf_counter() - inicio,
        )

        total_tratados = (
            lote_atualizado.processed_files
            + lote_atualizado.duplicated_files
            + lote_atualizado.failed_files
        )
        if lote_atualizado.total_files > 0 and total_tratados >= lote_atualizado.total_files:
            _registrar_metricas_finais_lote(lote_atualizado)

        logger.info(
            "Arquivo financeiro processado",
            extra={
                "batch_id": batch_id,
                "arquivo_nome": arquivo_nome,
                "etapa": "arquivo_concluido",
                "resultado": "failed",
                "duracao_segundos": round(perf_counter() - inicio, 3),
                "processados": lote_atualizado.processed_files,
                "duplicados": lote_atualizado.duplicated_files,
                "falhas": lote_atualizado.failed_files,
                "status_lote": lote_atualizado.status,
            },
        )

        return {
            "batch_id": lote_atualizado.id,
            "total": lote_atualizado.total_files,
            "processed": lote_atualizado.processed_files,
            "duplicated": lote_atualizado.duplicated_files,
            "failed": lote_atualizado.failed_files,
            "processed_count": lote_atualizado.processed_files,
            "duplicated_count": lote_atualizado.duplicated_files,
            "failed_count": lote_atualizado.failed_files,
            "status": lote_atualizado.status,
            "resultado_arquivo": "failed",
            "duracao_segundos": round(perf_counter() - inicio, 3),
        }

    logger.info(
        "Arquivo financeiro processado",
        extra={
            "batch_id": batch_id,
            "arquivo_nome": arquivo_nome,
            "etapa": "arquivo_concluido",
            "resultado": resultado_arquivo,
            "duracao_segundos": round(duracao_segundos, 3),
            "processados": lote_atualizado.processed_files,
            "duplicados": lote_atualizado.duplicated_files,
            "falhas": lote_atualizado.failed_files,
            "status_lote": lote_atualizado.status,
        },
    )

    return {
        "batch_id": lote_atualizado.id,
        "total": lote_atualizado.total_files,
        "processed": lote_atualizado.processed_files,
        "duplicated": lote_atualizado.duplicated_files,
        "failed": lote_atualizado.failed_files,
        "processed_count": lote_atualizado.processed_files,
        "duplicated_count": lote_atualizado.duplicated_files,
        "failed_count": lote_atualizado.failed_files,
        "status": lote_atualizado.status,
        "resultado_arquivo": resultado_arquivo,
        "duracao_segundos": round(duracao_segundos, 3),
    }


def processar_arquivo_financeiro_job(dados: dict) -> dict[str, object]:
    inicio = perf_counter()
    payload = ArquivoFinanceiroJobPayload.model_validate(dados)
    status_job = "finished"

    try:
        with SessionLocal() as db:
            lote = obter_lote_financeiro_por_id(db, payload.batch_id)
            if lote is None:
                raise ValueError("Lote financeiro nao encontrado.")

            logger.info(
                "Iniciando processamento de arquivo financeiro",
                extra={
                    "batch_id": payload.batch_id,
                    "arquivo_nome": payload.arquivo.arquivo_nome,
                    "etapa": "inicio_arquivo",
                    "total_arquivos": lote.total_files,
                },
            )
            resultado = _processar_arquivo_financeiro_job_em_db(
                db,
                batch_id=payload.batch_id,
                user_id=payload.user_id,
                arquivo_nome=payload.arquivo.arquivo_nome,
                caminho_temporario=payload.arquivo.arquivo_temporario_path,
                arquivo_hash=payload.arquivo.file_hash,
            )

            return resultado
    except Exception:
        status_job = "failed"
        raise
    finally:
        arquivo_temporario = Path(payload.arquivo.arquivo_temporario_path)
        try:
            os.unlink(arquivo_temporario)
        except FileNotFoundError:
            pass
        try:
            arquivo_temporario.parent.rmdir()
        except OSError:
            pass
        registrar_job_execucao(
            "financeiro_pdf",
            status_job,
            perf_counter() - inicio,
        )


def processar_lote_financeiro_job(dados: dict) -> dict[str, object]:
    inicio = perf_counter()
    payload = LoteFinanceiroJobPayload.model_validate(dados)
    status_job = "finished"

    try:
        with SessionLocal() as db:
            lote = obter_lote_financeiro_por_id(db, payload.batch_id)
            if lote is None:
                raise ValueError("Lote financeiro nao encontrado.")

            logger.info(
                "Iniciando processamento do lote financeiro",
                extra={
                    "batch_id": payload.batch_id,
                    "etapa": "inicio_lote",
                    "total_arquivos": len(payload.arquivos),
                },
            )
            atualizar_lote_financeiro(db, lote, status="processing")

            for arquivo in payload.arquivos:
                _processar_arquivo_financeiro_job_em_db(
                    db,
                    batch_id=payload.batch_id,
                    user_id=payload.user_id,
                    arquivo_nome=arquivo.arquivo_nome,
                    caminho_temporario=arquivo.arquivo_temporario_path,
                    arquivo_hash=arquivo.file_hash,
                )
                try:
                    os.unlink(arquivo.arquivo_temporario_path)
                except FileNotFoundError:
                    pass

            lote_final = obter_lote_financeiro_por_id(db, payload.batch_id)
            if lote_final is None:
                raise ValueError("Lote financeiro nao encontrado.")

            return {
                "batch_id": lote_final.id,
                "total": lote_final.total_files,
                "processed": lote_final.processed_files,
                "duplicated": lote_final.duplicated_files,
                "failed": lote_final.failed_files,
                "processed_count": lote_final.processed_files,
                "duplicated_count": lote_final.duplicated_files,
                "failed_count": lote_final.failed_files,
                "status": lote_final.status,
            }
    except Exception:
        status_job = "failed"
        raise
    finally:
        registrar_job_execucao(
            "financeiro_lote",
            status_job,
            perf_counter() - inicio,
        )


def _mediana_decimal(valores: list[Decimal]) -> Decimal:
    if not valores:
        return ZERO

    return Decimal(median(sorted(valores))).quantize(ZERO, rounding=ROUND_HALF_UP)


def _variacao_percentual_decimal(valor_inicial: Decimal, valor_final: Decimal) -> Decimal:
    if valor_inicial <= ZERO:
        return ZERO

    return ((valor_final - valor_inicial) / valor_inicial * Decimal("100")).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def _somar_itens_por_categoria(
    items: list[PaycheckItem],
) -> dict[str, Decimal]:
    totais = {categoria: ZERO for categoria in (*CATEGORIAS_VANTAGEM, *CATEGORIAS_DESCONTO)}

    for item in items:
        categoria = str(getattr(item, "categoria_normalizada", "") or "").strip()
        tipo = str(getattr(item, "tipo", "") or "").strip()
        if tipo == "vantagem":
            if categoria not in CATEGORIAS_VANTAGEM:
                categoria = "outros_vantagens"
        elif tipo == "desconto":
            if categoria not in CATEGORIAS_DESCONTO:
                categoria = "outros_descontos"
        else:
            continue

        totais[categoria] = totais[categoria] + _para_decimal(getattr(item, "valor", ZERO))

    return totais


def _mediana_por_categoria(valores_por_categoria: dict[str, list[Decimal]]) -> dict[str, Decimal]:
    return {
        categoria: _mediana_decimal(valores)
        for categoria, valores in valores_por_categoria.items()
    }


calcular_mediana_decimal = _mediana_decimal
calcular_variacao_percentual_decimal = _variacao_percentual_decimal


def _calcular_evolucao_salarial_a_partir_de_paychecks(
    paychecks: list[Paycheck],
    *,
    contexto_id: int | None,
) -> dict[str, object]:
    if not paychecks:
        return {
            "batch_id": contexto_id,
            "ano_inicial": None,
            "ano_final": None,
            "salario_base_inicial_referencia": None,
            "salario_base_final_referencia": None,
            "bruto_total_inicial_referencia": None,
            "bruto_total_final_referencia": None,
            "liquido_inicial_referencia": None,
            "liquido_final_referencia": None,
            "descontos_inicial_referencia": None,
            "descontos_final_referencia": None,
            "vantagens_adicionais_inicial_referencia": None,
            "vantagens_adicionais_final_referencia": None,
            "variacao_acumulada_salario_base_percentual": None,
            "anos_sem_crescimento_relevante": [],
            "series": [],
        }

    agrupados_por_ano: dict[int, list[Paycheck]] = defaultdict(list)
    for paycheck in paychecks:
        agrupados_por_ano[int(paycheck.ano)].append(paycheck)

    series_intermediarias: list[dict[str, object]] = []
    for ano in sorted(agrupados_por_ano):
        paychecks_ano = agrupados_por_ano[ano]
        salarios_base = [_para_decimal(item.vencimento_basico) for item in paychecks_ano]
        brutos_totais = [_para_decimal(item.bruto) for item in paychecks_ano]
        liquidos = [_para_decimal(item.liquido) for item in paychecks_ano]
        descontos = [_para_decimal(item.descontos) for item in paychecks_ano]
        valores_por_categoria_vantagem = {
            categoria: [] for categoria in CATEGORIAS_VANTAGEM
        }
        valores_por_categoria_desconto = {
            categoria: [] for categoria in CATEGORIAS_DESCONTO
        }

        for paycheck in paychecks_ano:
            totais_categoria = _somar_itens_por_categoria(list(paycheck.items))
            for categoria in CATEGORIAS_VANTAGEM:
                valores_por_categoria_vantagem[categoria].append(totais_categoria[categoria])
            for categoria in CATEGORIAS_DESCONTO:
                valores_por_categoria_desconto[categoria].append(totais_categoria[categoria])

        salario_base_referencia = _mediana_decimal(salarios_base)
        bruto_total_referencia = _mediana_decimal(brutos_totais)
        liquido_referencia = _mediana_decimal(liquidos)
        descontos_referencia = _mediana_decimal(descontos)
        vantagens_adicionais_referencia = (bruto_total_referencia - salario_base_referencia).quantize(
            ZERO,
            rounding=ROUND_HALF_UP,
        )
        series_intermediarias.append(
            {
                "ano": ano,
                "salario_base_referencia": salario_base_referencia,
                "bruto_total_referencia": bruto_total_referencia,
                "liquido_referencia": liquido_referencia,
                "descontos_referencia": descontos_referencia,
                "vantagens_adicionais_referencia": vantagens_adicionais_referencia,
                "composicao_vantagens_referencia": _mediana_por_categoria(
                    valores_por_categoria_vantagem
                ),
                "composicao_descontos_referencia": _mediana_por_categoria(
                    valores_por_categoria_desconto
                ),
                "quantidade_contracheques": len(paychecks_ano),
            }
        )

    anos_sem_crescimento_relevante: list[int] = []
    for indice, item in enumerate(series_intermediarias):
        if indice == 0:
            item["variacao_percentual_salario_base_ano_a_ano"] = None
            item["crescimento_relevante"] = True
            continue

        anterior = series_intermediarias[indice - 1]
        variacao_salario_base = _variacao_percentual_decimal(
            anterior["salario_base_referencia"],
            item["salario_base_referencia"],
        )
        item["variacao_percentual_salario_base_ano_a_ano"] = float(variacao_salario_base)
        item["crescimento_relevante"] = abs(variacao_salario_base) >= THRESHOLD_CRESCIMENTO_RELEVANTE
        if not item["crescimento_relevante"]:
            anos_sem_crescimento_relevante.append(int(item["ano"]))

    primeiro = series_intermediarias[0]
    ultimo = series_intermediarias[-1]
    ano_inicial = int(primeiro["ano"])
    ano_final = int(ultimo["ano"])
    variacao_acumulada_salario_base = _variacao_percentual_decimal(
        primeiro["salario_base_referencia"],
        ultimo["salario_base_referencia"],
    )

    series = [
        {
            "ano": int(item["ano"]),
            "salario_base_referencia_anual": float(item["salario_base_referencia"]),
            "bruto_total_referencia_anual": float(item["bruto_total_referencia"]),
            "liquido_referencia_anual": float(item["liquido_referencia"]),
            "descontos_referencia_anual": float(item["descontos_referencia"]),
            "vantagens_adicionais_referencia_anual": float(item["vantagens_adicionais_referencia"]),
            "composicao_vantagens_referencia_anual": {
                categoria: float(valor)
                for categoria, valor in item["composicao_vantagens_referencia"].items()
            },
            "composicao_descontos_referencia_anual": {
                categoria: float(valor)
                for categoria, valor in item["composicao_descontos_referencia"].items()
            },
            "quantidade_contracheques": int(item["quantidade_contracheques"]),
            "variacao_percentual_salario_base_ano_a_ano": item["variacao_percentual_salario_base_ano_a_ano"],
            "crescimento_relevante": bool(item["crescimento_relevante"]),
        }
        for item in series_intermediarias
    ]

    return {
        "batch_id": contexto_id,
        "ano_inicial": ano_inicial,
        "ano_final": ano_final,
        "salario_base_inicial_referencia": float(primeiro["salario_base_referencia"]),
        "salario_base_final_referencia": float(ultimo["salario_base_referencia"]),
        "bruto_total_inicial_referencia": float(primeiro["bruto_total_referencia"]),
        "bruto_total_final_referencia": float(ultimo["bruto_total_referencia"]),
        "liquido_inicial_referencia": float(primeiro["liquido_referencia"]),
        "liquido_final_referencia": float(ultimo["liquido_referencia"]),
        "descontos_inicial_referencia": float(primeiro["descontos_referencia"]),
        "descontos_final_referencia": float(ultimo["descontos_referencia"]),
        "vantagens_adicionais_inicial_referencia": float(primeiro["vantagens_adicionais_referencia"]),
        "vantagens_adicionais_final_referencia": float(ultimo["vantagens_adicionais_referencia"]),
        "variacao_acumulada_salario_base_percentual": float(variacao_acumulada_salario_base),
        "anos_sem_crescimento_relevante": anos_sem_crescimento_relevante,
        "series": series,
    }


def calcular_evolucao_salarial_lote(db: Session, batch_id: int) -> dict[str, object]:
    paychecks = obter_paychecks_por_batch_id(db, batch_id)
    return _calcular_evolucao_salarial_a_partir_de_paychecks(paychecks, contexto_id=batch_id)


def calcular_evolucao_salarial_por_usuario(db: Session, user_id: int) -> dict[str, object]:
    paychecks = obter_paychecks_por_usuario_id(db, user_id)
    contexto_id = int(paychecks[-1].batch_id) if paychecks else None
    return _calcular_evolucao_salarial_a_partir_de_paychecks(paychecks, contexto_id=contexto_id)
