from __future__ import annotations

from decimal import Decimal

from backend.database.database import SessionLocal
from backend.database.models import PayrollBatch, Paycheck
from backend.services.financeiro_batch_service import (
    calcular_cagr_percentual_decimal,
    calcular_evolucao_salarial_lote,
    calcular_mediana_decimal,
)


def _criar_lote_com_paychecks(registros: list[dict[str, object]]) -> int:
    with SessionLocal() as db:
        lote = PayrollBatch(
            user_id=7,
            total_files=len(registros),
            processed_files=len(registros),
            failed_files=0,
            status="completed",
        )
        db.add(lote)
        db.flush()

        for registro in registros:
            db.add(
                Paycheck(
                    batch_id=lote.id,
                    user_id=7,
                    competencia=str(registro["competencia"]),
                    ano=int(registro["ano"]),
                    mes=int(registro["mes"]),
                    bruto=Decimal(str(registro["bruto"])),
                    descontos=Decimal(str(registro["descontos"])),
                    liquido=Decimal(str(registro["liquido"])),
                    vencimento_basico=Decimal(str(registro["vencimento_basico"])),
                    adicional_desempenho=Decimal(str(registro["adicional_desempenho"])),
                    adicional_noturno=Decimal(str(registro["adicional_noturno"])),
                    irrf=Decimal(str(registro["irrf"])),
                    previdencia=Decimal(str(registro["previdencia"])),
                )
            )

        db.commit()
        return lote.id


def test_calcular_mediana_decimal_usa_mediana_em_vez_da_media() -> None:
    assert calcular_mediana_decimal(
        [
            Decimal("4000.00"),
            Decimal("4100.00"),
            Decimal("4200.00"),
            Decimal("13000.00"),
        ]
    ) == Decimal("4150.00")


def test_evolucao_salarial_anual_com_aumento_calcula_variacao_acumulada() -> None:
    batch_id = _criar_lote_com_paychecks(
        [
            {
                "competencia": "Janeiro/2022",
                "ano": 2022,
                "mes": 1,
                "bruto": "3900.00",
                "descontos": "500.00",
                "liquido": "3400.00",
                "vencimento_basico": "3000.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Fevereiro/2022",
                "ano": 2022,
                "mes": 2,
                "bruto": "4100.00",
                "descontos": "600.00",
                "liquido": "3500.00",
                "vencimento_basico": "3100.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Janeiro/2023",
                "ano": 2023,
                "mes": 1,
                "bruto": "4400.00",
                "descontos": "600.00",
                "liquido": "3800.00",
                "vencimento_basico": "3300.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Fevereiro/2023",
                "ano": 2023,
                "mes": 2,
                "bruto": "4600.00",
                "descontos": "700.00",
                "liquido": "3900.00",
                "vencimento_basico": "3400.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Janeiro/2024",
                "ano": 2024,
                "mes": 1,
                "bruto": "4900.00",
                "descontos": "700.00",
                "liquido": "4200.00",
                "vencimento_basico": "3700.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Fevereiro/2024",
                "ano": 2024,
                "mes": 2,
                "bruto": "5100.00",
                "descontos": "800.00",
                "liquido": "4300.00",
                "vencimento_basico": "3800.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
        ]
    )

    with SessionLocal() as db:
        resultado = calcular_evolucao_salarial_lote(db, batch_id)

    assert resultado["ano_inicial"] == 2022
    assert resultado["ano_final"] == 2024
    assert resultado["bruto_inicial_referencia"] == 4000.0
    assert resultado["bruto_final_referencia"] == 5000.0
    assert resultado["variacao_acumulada_bruto_percentual"] == 25.0
    assert resultado["cagr_bruto_percentual"] == 11.8
    assert resultado["series"][1]["variacao_percentual_bruto_ano_a_ano"] == 12.5
    assert resultado["series"][2]["variacao_percentual_bruto_ano_a_ano"] == 11.11
    assert resultado["anos_sem_crescimento_relevante"] == []


def test_evolucao_salarial_anual_sem_aumento_identifica_anos_sem_crescimento() -> None:
    batch_id = _criar_lote_com_paychecks(
        [
            {
                "competencia": "Janeiro/2022",
                "ano": 2022,
                "mes": 1,
                "bruto": "3900.00",
                "descontos": "500.00",
                "liquido": "3400.00",
                "vencimento_basico": "3000.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Fevereiro/2022",
                "ano": 2022,
                "mes": 2,
                "bruto": "4100.00",
                "descontos": "600.00",
                "liquido": "3500.00",
                "vencimento_basico": "3100.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Janeiro/2023",
                "ano": 2023,
                "mes": 1,
                "bruto": "3900.00",
                "descontos": "500.00",
                "liquido": "3400.00",
                "vencimento_basico": "3000.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Fevereiro/2023",
                "ano": 2023,
                "mes": 2,
                "bruto": "4100.00",
                "descontos": "600.00",
                "liquido": "3500.00",
                "vencimento_basico": "3100.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Janeiro/2024",
                "ano": 2024,
                "mes": 1,
                "bruto": "3900.00",
                "descontos": "500.00",
                "liquido": "3400.00",
                "vencimento_basico": "3000.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Fevereiro/2024",
                "ano": 2024,
                "mes": 2,
                "bruto": "4100.00",
                "descontos": "600.00",
                "liquido": "3500.00",
                "vencimento_basico": "3100.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
        ]
    )

    with SessionLocal() as db:
        resultado = calcular_evolucao_salarial_lote(db, batch_id)

    assert resultado["variacao_acumulada_bruto_percentual"] == 0.0
    assert resultado["cagr_bruto_percentual"] == 0.0
    assert resultado["series"][1]["variacao_percentual_bruto_ano_a_ano"] == 0.0
    assert resultado["series"][2]["variacao_percentual_bruto_ano_a_ano"] == 0.0
    assert resultado["anos_sem_crescimento_relevante"] == [2023, 2024]


def test_evolucao_salarial_anual_ignora_mes_atipico_na_mediana() -> None:
    batch_id = _criar_lote_com_paychecks(
        [
            {
                "competencia": "Janeiro/2024",
                "ano": 2024,
                "mes": 1,
                "bruto": "4000.00",
                "descontos": "500.00",
                "liquido": "3500.00",
                "vencimento_basico": "3000.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Fevereiro/2024",
                "ano": 2024,
                "mes": 2,
                "bruto": "4200.00",
                "descontos": "600.00",
                "liquido": "3600.00",
                "vencimento_basico": "3100.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Março/2024",
                "ano": 2024,
                "mes": 3,
                "bruto": "4100.00",
                "descontos": "550.00",
                "liquido": "3550.00",
                "vencimento_basico": "3050.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Dezembro/2024",
                "ano": 2024,
                "mes": 12,
                "bruto": "13000.00",
                "descontos": "3000.00",
                "liquido": "10000.00",
                "vencimento_basico": "3000.00",
                "adicional_desempenho": "200.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Janeiro/2025",
                "ano": 2025,
                "mes": 1,
                "bruto": "4500.00",
                "descontos": "650.00",
                "liquido": "3850.00",
                "vencimento_basico": "3250.00",
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "irrf": "50.00",
                "previdencia": "50.00",
            },
        ]
    )

    with SessionLocal() as db:
        resultado = calcular_evolucao_salarial_lote(db, batch_id)

    assert resultado["series"][0]["bruto_referencia_anual"] == 4150.0
    assert resultado["series"][0]["liquido_referencia_anual"] == 3575.0
    assert resultado["series"][0]["descontos_referencia_anual"] == 575.0


def test_cagr_percentual_decimal() -> None:
    assert calcular_cagr_percentual_decimal(
        Decimal("4000.00"),
        Decimal("6000.00"),
        2,
    ) == Decimal("22.47")
