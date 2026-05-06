from __future__ import annotations

from datetime import date, datetime, timezone
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routes import auth_routes


def criar_usuario_falso() -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        nome="Maria Silva",
        apelido="Maria",
        email="maria@example.com",
        data_exercicio=date(2020, 1, 1),
        login="maria",
        senha_cadastrada=True,
        email_confirmado=True,
        criado_em=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        confirmado_em=None,
    )


def criar_client() -> TestClient:
    app = FastAPI()
    app.include_router(auth_routes.router)
    app.dependency_overrides[auth_routes.get_db] = lambda: object()
    return TestClient(app)


def test_login_com_credenciais_corretas_retorna_200(monkeypatch) -> None:
    usuario = criar_usuario_falso()

    def autenticar_usuario_falso(db, dados):
        assert dados.login == "maria"
        assert dados.senha == "senha-segura"
        return usuario, "token-123"

    monkeypatch.setattr(auth_routes, "autenticar_usuario", autenticar_usuario_falso)

    client = criar_client()
    resposta = client.post(
        "/auth/login",
        json={"login": "maria", "senha": "senha-segura"},
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["access_token"] == "token-123"
    assert corpo["token_type"] == "bearer"
    assert corpo["usuario"]["id"] == 1
    assert corpo["usuario"]["nome"] == "Maria Silva"
    assert corpo["usuario"]["email"] == "maria@example.com"
    assert corpo["usuario"]["login"] == "maria"
    assert corpo["usuario"]["senha_cadastrada"] is True
    assert corpo["usuario"]["email_confirmado"] is True


def test_login_com_senha_errada_retorna_401(monkeypatch) -> None:
    def autenticar_usuario_falso(db, dados):
        raise ValueError("Senha incorreta.")

    monkeypatch.setattr(auth_routes, "autenticar_usuario", autenticar_usuario_falso)

    client = criar_client()
    resposta = client.post(
        "/auth/login",
        json={"login": "maria", "senha": "senha-errada"},
    )

    assert resposta.status_code == 401
    assert resposta.json() == {"detail": "Senha incorreta."}
