from __future__ import annotations

from decimal import Decimal

from backend.database.database import SessionLocal
from backend.database.models import PayrollBatch, Paycheck, PaycheckItem
from backend.services.financeiro_batch_service import (
    calcular_evolucao_salarial_lote,
    calcular_mediana_decimal,
)


def _item(tipo: str, categoria: str, descricao_original: str, valor: str) -> dict[str, object]:
    return {
        "tipo": tipo,
        "categoria_normalizada": categoria,
        "descricao_original": descricao_original,
        "descricao": descricao_original,
        "valor": Decimal(valor),
    }


def _vantagens_padrao(
    salario_base: str,
    *,
    ade: str = "300.00",
    adicional_noturno: str = "100.00",
    alimentacao: str = "200.00",
    abono_vestimenta: str = "50.00",
    outros_vantagens: str = "250.00",
    decimo_terceiro: str = "0.00",
    ferias: str = "0.00",
    retroativo: str = "0.00",
) -> list[dict[str, object]]:
    itens = [
        _item("vantagem", "salario_base", "Vencimento Basico", salario_base),
        _item("vantagem", "ade", "Adicional Desempenho", ade),
        _item("vantagem", "adicional_noturno", "Adic Not Divisor", adicional_noturno),
        _item("vantagem", "alimentacao", "Aj.custo/aliment", alimentacao),
        _item("vantagem", "abono_vestimenta", "Abono Aqu.vestimenta", abono_vestimenta),
        _item("vantagem", "outros_vantagens", "Outras vantagens", outros_vantagens),
    ]

    if Decimal(decimo_terceiro) > 0:
        itens.append(_item("vantagem", "decimo_terceiro", "13 Salario", decimo_terceiro))

    if Decimal(ferias) > 0:
        itens.append(_item("vantagem", "ferias", "Ferias", ferias))

    if Decimal(retroativo) > 0:
        itens.append(_item("vantagem", "retroativo", "Retroativo", retroativo))

    return itens


def _descontos_padrao(
    *,
    previdencia: str = "50.00",
    irrf: str = "200.00",
    emprestimo: str = "100.00",
    saude: str = "30.00",
    associacao: str = "10.00",
    outros_descontos: str = "10.00",
) -> list[dict[str, object]]:
    return [
        _item("desconto", "previdencia", "Contrib.prev.art. 28", previdencia),
        _item("desconto", "irrf", "Imp. Renda Ret.fonte", irrf),
        _item("desconto", "emprestimo", "B.pan - Emprest. i", emprestimo),
        _item("desconto", "saude", "Plano Saude", saude),
        _item("desconto", "associacao", "Associacao", associacao),
        _item("desconto", "outros_descontos", "Outros descontos", outros_descontos),
    ]


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
            paycheck = Paycheck(
                batch_id=lote.id,
                user_id=7,
                competencia=str(registro["competencia"]),
                ano=int(registro["ano"]),
                mes=int(registro["mes"]),
                bruto=Decimal(str(registro["bruto"])),
                descontos=Decimal(str(registro["descontos"])),
                liquido=Decimal(str(registro["liquido"])),
                vencimento_basico=Decimal(str(registro["salario_base"])),
                adicional_desempenho=Decimal(str(registro.get("adicional_desempenho", "0.00"))),
                adicional_noturno=Decimal(str(registro.get("adicional_noturno", "0.00"))),
                irrf=Decimal(str(registro.get("irrf", "0.00"))),
                previdencia=Decimal(str(registro.get("previdencia", "0.00"))),
            )
            db.add(paycheck)
            db.flush()

            for item in registro["itens"]:  # type: ignore[index]
                db.add(
                    PaycheckItem(
                        paycheck_id=paycheck.id,
                        tipo=str(item["tipo"]),
                        categoria_normalizada=str(item["categoria_normalizada"]),
                        descricao_original=str(item["descricao_original"]),
                        descricao=str(item["descricao"]),
                        valor=Decimal(str(item["valor"])),
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


def test_evolucao_financeira_anual_com_aumento_calcula_salario_base_e_composicao() -> None:
    batch_id = _criar_lote_com_paychecks(
        [
            {
                "competencia": "Janeiro/2022",
                "ano": 2022,
                "mes": 1,
                "salario_base": "3000.00",
                "bruto": "3900.00",
                "descontos": "500.00",
                "liquido": "3400.00",
                "itens": _vantagens_padrao("3000.00"),
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Fevereiro/2022",
                "ano": 2022,
                "mes": 2,
                "salario_base": "3100.00",
                "bruto": "4000.00",
                "descontos": "500.00",
                "liquido": "3500.00",
                "itens": _vantagens_padrao("3100.00"),
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Janeiro/2023",
                "ano": 2023,
                "mes": 1,
                "salario_base": "3200.00",
                "bruto": "4100.00",
                "descontos": "500.00",
                "liquido": "3600.00",
                "itens": _vantagens_padrao("3200.00"),
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Fevereiro/2023",
                "ano": 2023,
                "mes": 2,
                "salario_base": "3300.00",
                "bruto": "4200.00",
                "descontos": "500.00",
                "liquido": "3700.00",
                "itens": _vantagens_padrao("3300.00"),
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "previdencia": "50.00",
            },
            {
                "competencia": "Marco/2023",
                "ano": 2023,
                "mes": 3,
                "salario_base": "3400.00",
                "bruto": "4300.00",
                "descontos": "500.00",
                "liquido": "3800.00",
                "itens": _vantagens_padrao("3400.00"),
                "adicional_desempenho": "300.00",
                "adicional_noturno": "100.00",
                "previdencia": "50.00",
            },
        ]
    )

    with SessionLocal() as db:
        resultado = calcular_evolucao_salarial_lote(db, batch_id)

    assert resultado["ano_inicial"] == 2022
    assert resultado["ano_final"] == 2023
    assert resultado["salario_base_inicial_referencia"] == 3050.0
    assert resultado["salario_base_final_referencia"] == 3300.0
    assert resultado["bruto_total_inicial_referencia"] == 3950.0
    assert resultado["variacao_acumulada_salario_base_percentual"] == 8.2
    assert resultado["series"][0]["salario_base_referencia_anual"] == 3050.0
    assert resultado["series"][0]["bruto_total_referencia_anual"] == 3950.0
    assert resultado["series"][0]["vantagens_adicionais_referencia_anual"] == 900.0
    assert resultado["series"][0]["composicao_vantagens_referencia_anual"]["ade"] == 300.0
    assert resultado["series"][0]["composicao_descontos_referencia_anual"]["irrf"] == 200.0
    assert resultado["series"][1]["variacao_percentual_salario_base_ano_a_ano"] == 8.2
    assert resultado["anos_sem_crescimento_relevante"] == []


def test_evolucao_financeira_anual_sem_aumento_identifica_anos_sem_crescimento() -> None:
    batch_id = _criar_lote_com_paychecks(
        [
            {
                "competencia": "Janeiro/2022",
                "ano": 2022,
                "mes": 1,
                "salario_base": "3000.00",
                "bruto": "3900.00",
                "descontos": "500.00",
                "liquido": "3400.00",
                "itens": _vantagens_padrao("3000.00"),
            },
            {
                "competencia": "Fevereiro/2022",
                "ano": 2022,
                "mes": 2,
                "salario_base": "3100.00",
                "bruto": "4000.00",
                "descontos": "500.00",
                "liquido": "3500.00",
                "itens": _vantagens_padrao("3100.00"),
            },
            {
                "competencia": "Janeiro/2023",
                "ano": 2023,
                "mes": 1,
                "salario_base": "3000.00",
                "bruto": "3900.00",
                "descontos": "500.00",
                "liquido": "3400.00",
                "itens": _vantagens_padrao("3000.00"),
            },
            {
                "competencia": "Fevereiro/2023",
                "ano": 2023,
                "mes": 2,
                "salario_base": "3100.00",
                "bruto": "4000.00",
                "descontos": "500.00",
                "liquido": "3500.00",
                "itens": _vantagens_padrao("3100.00"),
            },
        ]
    )

    with SessionLocal() as db:
        resultado = calcular_evolucao_salarial_lote(db, batch_id)

    assert resultado["variacao_acumulada_salario_base_percentual"] == 0.0
    assert resultado["series"][1]["variacao_percentual_salario_base_ano_a_ano"] == 0.0
    assert resultado["anos_sem_crescimento_relevante"] == [2023]


def test_evolucao_financeira_anual_ignora_mes_atipico_na_mediana() -> None:
    batch_id = _criar_lote_com_paychecks(
        [
            {
                "competencia": "Janeiro/2024",
                "ano": 2024,
                "mes": 1,
                "salario_base": "3400.00",
                "bruto": "4300.00",
                "descontos": "500.00",
                "liquido": "3800.00",
                "itens": _vantagens_padrao("3400.00"),
            },
            {
                "competencia": "Fevereiro/2024",
                "ano": 2024,
                "mes": 2,
                "salario_base": "3450.00",
                "bruto": "4350.00",
                "descontos": "500.00",
                "liquido": "3850.00",
                "itens": _vantagens_padrao("3450.00"),
            },
            {
                "competencia": "Marco/2024",
                "ano": 2024,
                "mes": 3,
                "salario_base": "3450.00",
                "bruto": "4400.00",
                "descontos": "500.00",
                "liquido": "3900.00",
                "itens": _vantagens_padrao("3450.00"),
            },
            {
                "competencia": "Dezembro/2024",
                "ano": 2024,
                "mes": 12,
                "salario_base": "3450.00",
                "bruto": "13000.00",
                "descontos": "3000.00",
                "liquido": "10000.00",
                "itens": _vantagens_padrao(
                    "3450.00",
                    decimo_terceiro="8000.00",
                    outros_vantagens="900.00",
                ),
            },
        ]
    )

    with SessionLocal() as db:
        resultado = calcular_evolucao_salarial_lote(db, batch_id)

    assert resultado["series"][0]["salario_base_referencia_anual"] == 3450.0
    assert resultado["series"][0]["bruto_total_referencia_anual"] == 4375.0
    assert resultado["series"][0]["salario_base_referencia_anual"] != resultado["series"][0]["bruto_total_referencia_anual"]
