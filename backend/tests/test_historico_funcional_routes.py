from __future__ import annotations

from datetime import date
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routes import historico_funcional_routes


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
        return SimpleNamespace(id="job-123")


def criar_client() -> TestClient:
    app = FastAPI()
    app.include_router(historico_funcional_routes.router)
    app.dependency_overrides[historico_funcional_routes.get_db] = lambda: object()
    app.dependency_overrides[historico_funcional_routes.obter_usuario_autenticado] = lambda: SimpleNamespace(id=7)
    return TestClient(app)


def test_upload_pdf_valido_eh_aceito(monkeypatch) -> None:
    fila_falsa = FilaFalsa()
    chamadas: dict[str, object] = {}

    def gerar_caminho_falso(nome_arquivo: str, usuario_id: int | None) -> str:
        chamadas["gerar_caminho"] = (nome_arquivo, usuario_id)
        return "historicos/usuario-7/historico.pdf"

    def enviar_pdf_falso(conteudo_pdf: bytes, caminho_storage: str, content_type: str = "application/pdf"):
        chamadas["upload"] = (conteudo_pdf, caminho_storage, content_type)
        return SimpleNamespace(caminho_storage=caminho_storage, origem="local")

    monkeypatch.setattr(
        historico_funcional_routes,
        "gerar_caminho_storage_historico",
        gerar_caminho_falso,
    )
    monkeypatch.setattr(
        historico_funcional_routes,
        "enviar_pdf_para_storage",
        enviar_pdf_falso,
    )
    monkeypatch.setattr(
        historico_funcional_routes,
        "obter_fila_historicos",
        lambda: fila_falsa,
    )

    client = criar_client()
    resposta = client.post(
        "/historicos-funcionais/analisar",
        data={
            "data_nascimento": "1980-01-01",
            "sexo": "feminino",
            "categoria_previdenciaria": "professor",
            "anos_clt_averbados": "2",
            "usuario_id": "999",
        },
        files={
            "arquivo": (
                "historico.pdf",
                b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF",
                "application/pdf",
            )
        },
    )

    assert resposta.status_code == 201
    assert resposta.json() == {
        "job_id": "job-123",
        "status": "queued",
        "detail": "Seu PDF foi recebido e esta sendo processado em segundo plano.",
    }
    assert chamadas["gerar_caminho"] == ("historico.pdf", 7)
    assert chamadas["upload"][0].startswith(b"%PDF")
    assert chamadas["upload"][1] == "historicos/usuario-7/historico.pdf"
    assert chamadas["upload"][2] == "application/pdf"
    assert fila_falsa.chamadas[0]["funcao"] == "processar_historico_funcional_job"


def test_historico_funcional_de_outro_usuario_e_bloqueado() -> None:
    client = criar_client()
    resposta = client.get("/historicos-funcionais/usuario/8/ultimo")

    assert resposta.status_code == 403
