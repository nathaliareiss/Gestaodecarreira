from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.database.database import SessionLocal
from backend.database.models import FinanceiroImportacaoTemporaria, PayrollBatch
from backend.routes import financeiro_routes


FIXTURE_PDF = Path(__file__).parent / "fixtures" / "contracheque_exemplo.pdf"


def get_db_teste():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def criar_client() -> TestClient:
    app = FastAPI()
    app.include_router(financeiro_routes.router)
    app.dependency_overrides[financeiro_routes.get_db] = get_db_teste
    app.dependency_overrides[financeiro_routes.obter_usuario_autenticado] = lambda: SimpleNamespace(id=7)
    return TestClient(app)


def test_criar_validar_e_usar_importacao_temporaria_financeira(monkeypatch) -> None:
    monkeypatch.setattr(financeiro_routes, "obter_fila_financeiro", lambda: None)

    client = criar_client()

    resposta_criacao = client.post("/financeiro/importacao-temporaria")
    assert resposta_criacao.status_code == 201
    payload_criacao = resposta_criacao.json()
    assert payload_criacao["scope"] == "financeiro_importacao"
    assert payload_criacao["token"]
    assert payload_criacao["expires_at"]

    with SessionLocal() as db:
        importacao = db.query(FinanceiroImportacaoTemporaria).one()
        assert importacao.user_id == 7
        assert importacao.used_at is None

    resposta_validacao = client.post(
        "/financeiro/importacao-temporaria/validar",
        json={"token": payload_criacao["token"]},
    )
    assert resposta_validacao.status_code == 200
    assert resposta_validacao.json()["valid"] is True
    assert resposta_validacao.json()["user_id"] == 7
    assert resposta_validacao.json()["used"] is False

    with FIXTURE_PDF.open("rb") as arquivo:
        resposta_upload = client.post(
            "/financeiro/importacao-temporaria/upload-lote",
            headers={"X-Import-Token": payload_criacao["token"]},
            files=[("arquivos", ("01-2025_Mensal.pdf", arquivo.read(), "application/pdf"))],
        )

    assert resposta_upload.status_code == 201
    assert resposta_upload.json()["status"] == "completed"

    with SessionLocal() as db:
        lote = db.query(PayrollBatch).order_by(PayrollBatch.id.desc()).first()
        assert lote is not None
        assert lote.user_id == 7

        importacao = db.query(FinanceiroImportacaoTemporaria).one()
        assert importacao.used_at is not None

    resposta_validacao_depois = client.post(
        "/financeiro/importacao-temporaria/validar",
        json={"token": payload_criacao["token"]},
    )
    assert resposta_validacao_depois.status_code == 401
