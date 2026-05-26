from __future__ import annotations

from datetime import date, datetime, timezone
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routes import usuario_routes


def criar_usuario_falso() -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        nome="Maria Silva",
        apelido="Maria",
        email="maria@example.com",
        data_exercicio=date(2020, 1, 1),
        login="maria",
        senha_cadastrada=True,
        email_confirmado=False,
        token_confirmacao_email="token-confirmacao",
        criado_em=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        confirmado_em=None,
    )


def criar_client() -> TestClient:
    app = FastAPI()
    app.include_router(usuario_routes.router)
    app.dependency_overrides[usuario_routes.get_db] = lambda: object()
    return TestClient(app)


def test_criar_usuario_novo_retorna_201(monkeypatch) -> None:
    usuario = criar_usuario_falso()

    def cadastrar_usuario_falso(db, cadastro):
        assert cadastro.email == "novo@example.com"
        assert cadastro.login == "novo.login"
        return usuario

    monkeypatch.setattr(usuario_routes, "cadastrar_usuario", cadastrar_usuario_falso)
    monkeypatch.setattr(usuario_routes, "enviar_email_confirmacao", lambda **kwargs: None)

    client = criar_client()
    resposta = client.post(
        "/usuarios",
        json={
            "nome": "Maria Silva",
            "apelido": "Maria",
            "email": "novo@example.com",
            "data_exercicio": "2020-01-01",
            "login": "novo.login",
            "senha": "senha-segura",
        },
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id"] == 1
    assert corpo["email"] == "maria@example.com"
    assert corpo["email_confirmado"] is False


def test_criar_usuario_email_duplicado_retorna_409(monkeypatch) -> None:
    def cadastrar_usuario_falso(db, cadastro):
        raise ValueError("Ja existe um usuario cadastrado com este email.")

    monkeypatch.setattr(usuario_routes, "cadastrar_usuario", cadastrar_usuario_falso)

    client = criar_client()
    resposta = client.post(
        "/usuarios",
        json={
            "nome": "Maria Silva",
            "apelido": "Maria",
            "email": "maria@example.com",
            "data_exercicio": "2020-01-01",
            "login": "novo.login",
            "senha": "senha-segura",
        },
    )

    assert resposta.status_code == 409
    assert resposta.json() == {"detail": "Ja existe um usuario cadastrado com este email."}


def test_criar_usuario_falha_tecnica_retorna_503(monkeypatch) -> None:
    def cadastrar_usuario_falso(db, cadastro):
        raise RuntimeError("database indisponivel")

    monkeypatch.setattr(usuario_routes, "cadastrar_usuario", cadastrar_usuario_falso)

    client = criar_client()
    resposta = client.post(
        "/usuarios",
        json={
            "nome": "Maria Silva",
            "apelido": "Maria",
            "email": "novo@example.com",
            "data_exercicio": "2020-01-01",
            "login": "novo.login",
            "senha": "senha-segura",
        },
    )

    assert resposta.status_code == 503
    assert resposta.json() == {
        "detail": "Nao foi possivel concluir o cadastro agora. Tente novamente mais tarde."
    }
