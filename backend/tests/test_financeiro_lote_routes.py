from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.database.database import SessionLocal
from backend.database.models import PayrollBatch
from backend.routes import financeiro_routes


FIXTURE_PDF = Path(__file__).parent / "fixtures" / "contracheque_exemplo.pdf"


class FilaFalsa:
    def __init__(self) -> None:
        self.chamadas: list[dict[str, object]] = []

    def enqueue(self, func, dados, job_timeout):
        self.chamadas.append(
            {
                "funcao": func.__name__,
                "dados": dados,
                "job_timeout": job_timeout,
            }
        )
        return SimpleNamespace(id="job-fin-123")


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
    return TestClient(app)


def test_upload_lote_financeiro_agenda_job_e_cria_batch(monkeypatch) -> None:
    fila_falsa = FilaFalsa()
    monkeypatch.setattr(financeiro_routes, "obter_fila_financeiro", lambda: fila_falsa)

    client = criar_client()
    with FIXTURE_PDF.open("rb") as arquivo1, FIXTURE_PDF.open("rb") as arquivo2:
        resposta = client.post(
            "/financeiro/upload-lote",
            data={"user_id": "7"},
            files=[
                ("arquivos", ("01-2025_Mensal.pdf", arquivo1.read(), "application/pdf")),
                ("arquivos", ("02-2025_Mensal.pdf", arquivo2.read(), "application/pdf")),
            ],
        )

    assert resposta.status_code == 201
    assert resposta.json() == {"batch_id": 1, "status": "processing"}
    assert fila_falsa.chamadas[0]["funcao"] == "processar_lote_financeiro_job"
    assert len(fila_falsa.chamadas[0]["dados"]["arquivos"]) == 2

    with SessionLocal() as db:
        lote = db.get(PayrollBatch, 1)
        assert lote is not None
        assert lote.total_files == 2
        assert lote.status == "processing"


def test_upload_lote_financeiro_processa_diretamente_quando_fila_ausente(monkeypatch) -> None:
    monkeypatch.setattr(financeiro_routes, "obter_fila_financeiro", lambda: None)

    client = criar_client()
    with FIXTURE_PDF.open("rb") as arquivo:
        resposta = client.post(
            "/financeiro/upload-lote",
            data={"user_id": "7"},
            files=[("arquivos", ("01-2025_Mensal.pdf", arquivo.read(), "application/pdf"))],
        )

    assert resposta.status_code == 201
    assert resposta.json() == {"batch_id": 1, "status": "completed"}

    with SessionLocal() as db:
        lote = db.get(PayrollBatch, 1)
        assert lote is not None
        assert lote.total_files == 1
        assert lote.status == "completed"
        assert lote.processed_files == 1
        assert lote.failed_files == 0


def test_evolucao_salarial_por_lote_sem_contracheques_retorna_404() -> None:
    with SessionLocal() as db:
        lote = PayrollBatch(
            user_id=7,
            total_files=1,
            processed_files=0,
            failed_files=0,
            status="completed",
        )
        db.add(lote)
        db.commit()

    client = criar_client()
    resposta = client.get(f"/financeiro/batch/{lote.id}/evolucao-salarial")

    assert resposta.status_code == 404
    assert resposta.json() == {
        "detail": "Nenhum contracheque processado foi encontrado para este lote."
    }
