from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.database.database import SessionLocal
from backend.database.models import PayrollBatch, Paycheck, PaycheckItem
from backend.routes import financeiro_routes


FIXTURE_PDF = Path(__file__).parent / "fixtures" / "contracheque_exemplo.pdf"


def criar_client() -> TestClient:
    app = FastAPI()
    app.include_router(financeiro_routes.router)
    app.dependency_overrides[financeiro_routes.obter_usuario_autenticado] = lambda: SimpleNamespace(id=7)
    return TestClient(app)


def test_analisar_contracheque_retorna_json_estruturado() -> None:
    client = criar_client()

    with FIXTURE_PDF.open("rb") as arquivo:
        resposta = client.post(
            "/financeiro/contracheque/analisar",
            files={
                "arquivo": (
                    "contracheque_exemplo.pdf",
                    arquivo.read(),
                    "application/pdf",
                )
            },
        )

    assert resposta.status_code == 200
    assert resposta.json() == {
        "competencia": "Janeiro/2022",
        "ano": 2022,
        "mes": 1,
        "matricula": "",
        "bruto": "5375.07",
        "descontos": "550.00",
        "liquido": "4825.07",
        "vencimento_basico": "5000.00",
        "adicional_desempenho": "300.00",
        "adicional_noturno": "75.07",
        "irrf": "200.00",
        "previdencia": "350.00",
    }


def _criar_lote_com_paychecks(user_id: int, registros: list[dict[str, object]]) -> int:
    with SessionLocal() as db:
        lote = PayrollBatch(
            user_id=user_id,
            total_files=len(registros),
            processed_files=len(registros),
            failed_files=0,
            status="completed",
        )
        db.add(lote)
        db.flush()

        for registro in registros:
            salario_base = Decimal(str(registro["salario_base"]))
            paycheck = Paycheck(
                batch_id=lote.id,
                user_id=user_id,
                competencia=str(registro["competencia"]),
                ano=int(registro["ano"]),
                mes=int(registro["mes"]),
                bruto=Decimal(str(registro["bruto"])),
                descontos=Decimal(str(registro["descontos"])),
                liquido=Decimal(str(registro["liquido"])),
                vencimento_basico=salario_base,
                adicional_desempenho=Decimal(str(registro.get("adicional_desempenho", "0.00"))),
                adicional_noturno=Decimal(str(registro.get("adicional_noturno", "0.00"))),
                irrf=Decimal(str(registro.get("irrf", "0.00"))),
                previdencia=Decimal(str(registro.get("previdencia", "0.00"))),
            )
            db.add(paycheck)
            db.flush()
            db.add(
                PaycheckItem(
                    paycheck_id=paycheck.id,
                    tipo="vantagem",
                    categoria_normalizada="salario_base",
                    descricao_original="Vencimento Basico",
                    descricao="Vencimento Basico",
                    valor=salario_base,
                )
            )

        db.commit()
        return lote.id


def _criar_batch_vazio(user_id: int, status: str = "processing") -> int:
    with SessionLocal() as db:
        lote = PayrollBatch(
            user_id=user_id,
            total_files=1,
            processed_files=0,
            failed_files=0,
            status=status,
        )
        db.add(lote)
        db.commit()
        return lote.id


def test_evolucao_salarial_persistida_busca_dados_salvos_do_usuario() -> None:
    _criar_lote_com_paychecks(
        7,
        [
            {
                "competencia": "Janeiro/2022",
                "ano": 2022,
                "mes": 1,
                "salario_base": "3000.00",
                "bruto": "3900.00",
                "descontos": "500.00",
                "liquido": "3400.00",
            },
            {
                "competencia": "Janeiro/2023",
                "ano": 2023,
                "mes": 1,
                "salario_base": "3200.00",
                "bruto": "4100.00",
                "descontos": "500.00",
                "liquido": "3600.00",
            },
        ],
    )
    _criar_batch_vazio(7, status="processing")

    client = criar_client()
    resposta = client.get("/financeiro/evolucao-salarial")

    assert resposta.status_code == 200
    payload = resposta.json()
    assert payload["ano_inicial"] == 2022
    assert payload["ano_final"] == 2023
    assert payload["salario_base_inicial_referencia"] == 3000.0
    assert payload["salario_base_final_referencia"] == 3200.0
    assert payload["series"][0]["salario_base_referencia_anual"] == 3000.0


def test_contracheques_salvos_isolados_por_usuario() -> None:
    _criar_lote_com_paychecks(
        7,
        [
            {
                "competencia": "Janeiro/2024",
                "ano": 2024,
                "mes": 1,
                "salario_base": "3100.00",
                "bruto": "4000.00",
                "descontos": "500.00",
                "liquido": "3500.00",
            },
        ],
    )
    _criar_lote_com_paychecks(
        8,
        [
            {
                "competencia": "Fevereiro/2024",
                "ano": 2024,
                "mes": 2,
                "salario_base": "4200.00",
                "bruto": "5300.00",
                "descontos": "700.00",
                "liquido": "4600.00",
            },
        ],
    )

    client = criar_client()
    resposta = client.get("/financeiro/contracheques")

    assert resposta.status_code == 200
    payload = resposta.json()
    assert len(payload) == 1
    assert payload[0]["competencia"] == "Janeiro/2024"
    assert payload[0]["salario_base"] == 3100.0
    assert payload[0]["bruto_total"] == 4000.0


def test_evolucao_salarial_persistida_nao_depende_do_batch_atual() -> None:
    _criar_lote_com_paychecks(
        7,
        [
            {
                "competencia": "Janeiro/2021",
                "ano": 2021,
                "mes": 1,
                "salario_base": "2800.00",
                "bruto": "3600.00",
                "descontos": "400.00",
                "liquido": "3200.00",
            },
        ],
    )
    _criar_batch_vazio(7, status="failed")

    client = criar_client()
    resposta = client.get("/financeiro/evolucao-salarial")

    assert resposta.status_code == 200
    payload = resposta.json()
    assert payload["ano_inicial"] == 2021
    assert payload["series"][0]["salario_base_referencia_anual"] == 2800.0
