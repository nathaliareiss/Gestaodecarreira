from __future__ import annotations

import os
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from math import pow
from time import perf_counter
from statistics import median

from sqlalchemy.orm import Session

from backend.database.database import SessionLocal
from backend.database.models import Paycheck, PaycheckItem
from backend.logger import logger
from backend.metrics import registrar_job_execucao
from backend.repositories.financeiro_repository import (
    atualizar_lote_financeiro,
    existe_paycheck_por_competencia,
    obter_lote_financeiro_por_id,
    obter_paychecks_por_batch_id,
    salvar_paycheck_com_itens,
)
from backend.schemas.financeiro_schema import LoteFinanceiroJobPayload
from backend.services.contracheque_parser import (
    extrair_rubricas_contracheque,
    parse_contracheque,
)

ZERO = Decimal("0.00")
THRESHOLD_CRESCIMENTO_RELEVANTE = Decimal("1.00")


def _para_decimal(valor: object) -> Decimal:
    if isinstance(valor, Decimal):
        return valor

    if valor is None or valor == "":
        return ZERO

    return Decimal(str(valor))


def _criar_paycheck_item(payload: dict[str, object]) -> PaycheckItem:
    return PaycheckItem(
        tipo=str(payload["tipo"]),
        descricao=str(payload["descricao"]),
        valor=_para_decimal(payload["valor"]),
    )


def _criar_paycheck_model(
    batch_id: int,
    user_id: int | None,
    dados: dict[str, object],
) -> Paycheck:
    competencia = str(dados.get("competencia") or "").strip()
    ano = int(dados.get("ano") or 0)
    mes = int(dados.get("mes") or 0)

    if not competencia or ano <= 0 or mes <= 0:
        raise ValueError("Nao foi possivel identificar a competencia do contracheque.")

    return Paycheck(
        batch_id=batch_id,
        user_id=user_id,
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
) -> None:
    dados = parse_contracheque(caminho_temporario)
    rubricas = extrair_rubricas_contracheque(caminho_temporario)
    paycheck = _criar_paycheck_model(batch_id, user_id, dados)

    if user_id is not None and existe_paycheck_por_competencia(db, user_id, paycheck.competencia):
        raise ValueError(
            f"Já existe um contracheque salvo para a competência {paycheck.competencia}."
        )

    itens = [_criar_paycheck_item(item) for item in rubricas]
    salvar_paycheck_com_itens(db, paycheck, itens)
    logger.info(
        "Contracheque financeiro salvo",
        extra={
            "batch_id": batch_id,
            "arquivo_nome": arquivo_nome,
            "competencia": paycheck.competencia,
        },
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

            atualizar_lote_financeiro(db, lote, status="processing")

            for arquivo in payload.arquivos:
                try:
                    _processar_arquivo_individual(
                        db=db,
                        batch_id=payload.batch_id,
                        user_id=payload.user_id,
                        arquivo_nome=arquivo.arquivo_nome,
                        caminho_temporario=arquivo.arquivo_temporario_path,
                    )
                    atualizar_lote_financeiro(db, lote, processed_delta=1)
                except Exception as erro_arquivo:
                    db.rollback()
                    logger.warning(
                        "Falha ao processar contracheque do lote",
                        extra={
                            "batch_id": payload.batch_id,
                            "arquivo_nome": arquivo.arquivo_nome,
                            "erro": str(erro_arquivo),
                        },
                    )
                    atualizar_lote_financeiro(db, lote, failed_delta=1)
                finally:
                    try:
                        os.unlink(arquivo.arquivo_temporario_path)
                    except FileNotFoundError:
                        pass

            lote_atualizado = obter_lote_financeiro_por_id(db, payload.batch_id)
            if lote_atualizado is not None:
                status_final = "failed" if lote_atualizado.processed_files == 0 else "completed"
                atualizar_lote_financeiro(db, lote_atualizado, status=status_final)

            lote_final = obter_lote_financeiro_por_id(db, payload.batch_id)
            if lote_final is None:
                raise ValueError("Lote financeiro nao encontrado.")

            return {
                "batch_id": lote_final.id,
                "total": lote_final.total_files,
                "processed": lote_final.processed_files,
                "failed": lote_final.failed_files,
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


def _cagr_percentual_decimal(valor_inicial: Decimal, valor_final: Decimal, periodos: int) -> Decimal:
    if valor_inicial <= ZERO or valor_final <= ZERO or periodos <= 0:
        return ZERO

    crescimento = (pow(float(valor_final / valor_inicial), 1 / periodos) - 1) * 100
    return Decimal(str(crescimento)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


calcular_mediana_decimal = _mediana_decimal
calcular_variacao_percentual_decimal = _variacao_percentual_decimal
calcular_cagr_percentual_decimal = _cagr_percentual_decimal


def calcular_evolucao_salarial_lote(db: Session, batch_id: int) -> dict[str, object]:
    paychecks = obter_paychecks_por_batch_id(db, batch_id)
    if not paychecks:
        raise ValueError("Nenhum contracheque processado foi encontrado para este lote.")

    agrupados_por_ano: dict[int, list[Paycheck]] = defaultdict(list)
    for paycheck in paychecks:
        agrupados_por_ano[int(paycheck.ano)].append(paycheck)

    series_intermediarias: list[dict[str, object]] = []
    for ano in sorted(agrupados_por_ano):
        paychecks_ano = agrupados_por_ano[ano]
        bruto_referencia = _mediana_decimal([_para_decimal(item.bruto) for item in paychecks_ano])
        liquido_referencia = _mediana_decimal([_para_decimal(item.liquido) for item in paychecks_ano])
        descontos_referencia = _mediana_decimal([_para_decimal(item.descontos) for item in paychecks_ano])
        series_intermediarias.append(
            {
                "ano": ano,
                "bruto_referencia": bruto_referencia,
                "liquido_referencia": liquido_referencia,
                "descontos_referencia": descontos_referencia,
                "quantidade_contracheques": len(paychecks_ano),
            }
        )

    anos_sem_crescimento_relevante: list[int] = []
    for indice, item in enumerate(series_intermediarias):
        if indice == 0:
            item["variacao_percentual_bruto_ano_a_ano"] = None
            item["variacao_percentual_liquido_ano_a_ano"] = None
            item["crescimento_relevante"] = True
            continue

        anterior = series_intermediarias[indice - 1]
        variacao_bruto = _variacao_percentual_decimal(
            anterior["bruto_referencia"],
            item["bruto_referencia"],
        )
        variacao_liquido = _variacao_percentual_decimal(
            anterior["liquido_referencia"],
            item["liquido_referencia"],
        )
        item["variacao_percentual_bruto_ano_a_ano"] = float(variacao_bruto)
        item["variacao_percentual_liquido_ano_a_ano"] = float(variacao_liquido)
        item["crescimento_relevante"] = abs(variacao_bruto) >= THRESHOLD_CRESCIMENTO_RELEVANTE
        if not item["crescimento_relevante"]:
            anos_sem_crescimento_relevante.append(int(item["ano"]))

    primeiro = series_intermediarias[0]
    ultimo = series_intermediarias[-1]
    ano_inicial = int(primeiro["ano"])
    ano_final = int(ultimo["ano"])
    periodos = max(ano_final - ano_inicial, 0)

    variacao_acumulada_bruto = _variacao_percentual_decimal(
        primeiro["bruto_referencia"],
        ultimo["bruto_referencia"],
    )
    variacao_acumulada_liquido = _variacao_percentual_decimal(
        primeiro["liquido_referencia"],
        ultimo["liquido_referencia"],
    )
    cagr_bruto = _cagr_percentual_decimal(
        primeiro["bruto_referencia"],
        ultimo["bruto_referencia"],
        periodos,
    )
    cagr_liquido = _cagr_percentual_decimal(
        primeiro["liquido_referencia"],
        ultimo["liquido_referencia"],
        periodos,
    )

    series = [
        {
            "ano": int(item["ano"]),
            "bruto_referencia_anual": float(item["bruto_referencia"]),
            "liquido_referencia_anual": float(item["liquido_referencia"]),
            "descontos_referencia_anual": float(item["descontos_referencia"]),
            "quantidade_contracheques": int(item["quantidade_contracheques"]),
            "variacao_percentual_bruto_ano_a_ano": item["variacao_percentual_bruto_ano_a_ano"],
            "variacao_percentual_liquido_ano_a_ano": item["variacao_percentual_liquido_ano_a_ano"],
            "crescimento_relevante": bool(item["crescimento_relevante"]),
        }
        for item in series_intermediarias
    ]

    return {
        "batch_id": batch_id,
        "ano_inicial": ano_inicial,
        "ano_final": ano_final,
        "bruto_inicial_referencia": float(primeiro["bruto_referencia"]),
        "bruto_final_referencia": float(ultimo["bruto_referencia"]),
        "liquido_inicial_referencia": float(primeiro["liquido_referencia"]),
        "liquido_final_referencia": float(ultimo["liquido_referencia"]),
        "descontos_inicial_referencia": float(primeiro["descontos_referencia"]),
        "descontos_final_referencia": float(ultimo["descontos_referencia"]),
        "variacao_acumulada_bruto_percentual": float(variacao_acumulada_bruto),
        "variacao_acumulada_liquido_percentual": float(variacao_acumulada_liquido),
        "cagr_bruto_percentual": float(cagr_bruto),
        "cagr_liquido_percentual": float(cagr_liquido),
        "anos_sem_crescimento_relevante": anos_sem_crescimento_relevante,
        "series": series,
    }
