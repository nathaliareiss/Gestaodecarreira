from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routes.financeiro_routes import router as financeiro_router


FIXTURE_PDF = Path(__file__).parent / "fixtures" / "contracheque_exemplo.pdf"


def criar_client() -> TestClient:
    app = FastAPI()
    app.include_router(financeiro_router)
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
        "bruto": "5375.07",
        "descontos": "550.00",
        "liquido": "4825.07",
        "vencimento_basico": "5000.00",
        "adicional_desempenho": "300.00",
        "adicional_noturno": "75.07",
        "irrf": "200.00",
        "previdencia": "350.00",
    }
