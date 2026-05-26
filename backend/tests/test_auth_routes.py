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
    assert corpo["usuario"]["id"] == 1
    assert corpo["usuario"]["nome"] == "Maria Silva"
    assert corpo["usuario"]["email"] == "maria@example.com"
    assert corpo["usuario"]["login"] == "maria"
    assert corpo["usuario"]["senha_cadastrada"] is True
    assert corpo["usuario"]["email_confirmado"] is True
    assert "gc_auth_token=" in resposta.headers.get("set-cookie", "")


def test_login_cross_origin_em_https_usa_samesite_none(monkeypatch) -> None:
    usuario = criar_usuario_falso()

    def autenticar_usuario_falso(db, dados):
        return usuario, "token-123"

    monkeypatch.setattr(auth_routes, "autenticar_usuario", autenticar_usuario_falso)
    monkeypatch.setattr(auth_routes, "FRONTEND_BASE_URL", "https://frontend.example.com")

    app = FastAPI()
    app.include_router(auth_routes.router)
    app.dependency_overrides[auth_routes.get_db] = lambda: object()
    client = TestClient(app, base_url="https://api.example.com")

    resposta = client.post(
        "/auth/login",
        json={"login": "maria", "senha": "senha-segura"},
    )

    set_cookie = resposta.headers.get("set-cookie", "").lower()
    assert resposta.status_code == 200
    assert "gc_auth_token=" in set_cookie
    assert "samesite=none" in set_cookie
    assert "secure" in set_cookie


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


def test_solicitar_recuperacao_senha_retorna_200(monkeypatch) -> None:
    usuario = criar_usuario_falso()

    def solicitar_recuperacao_falso(db, dados):
        assert dados.email == "maria@example.com"
        return usuario, "token-redefinicao"

    monkeypatch.setattr(auth_routes, "solicitar_recuperacao_senha", solicitar_recuperacao_falso)
    monkeypatch.setattr(auth_routes, "enviar_email_recuperacao_senha", lambda **kwargs: None)

    client = criar_client()
    resposta = client.post(
        "/auth/solicitar-recuperacao-senha",
        json={"email": "maria@example.com"},
    )

    assert resposta.status_code == 200
    assert resposta.json() == {
        "status": "ok",
        "message": "Se o email estiver cadastrado, voce vai receber o link de redefinicao.",
    }


def test_solicitar_recuperacao_senha_email_nao_cadastrado_retorna_200(monkeypatch) -> None:
    def solicitar_recuperacao_falso(db, dados):
        raise ValueError("Nao encontramos um usuario cadastrado com este email.")

    monkeypatch.setattr(auth_routes, "solicitar_recuperacao_senha", solicitar_recuperacao_falso)

    client = criar_client()
    resposta = client.post(
        "/auth/solicitar-recuperacao-senha",
        json={"email": "inexistente@example.com"},
    )

    assert resposta.status_code == 200
    assert resposta.json() == {
        "status": "ok",
        "message": "Se o email estiver cadastrado, voce vai receber o link de redefinicao.",
    }


def test_solicitar_recuperacao_senha_falha_tecnica_retorna_503(monkeypatch) -> None:
    def solicitar_recuperacao_falso(db, dados):
        raise RuntimeError("smtp fora do ar")

    monkeypatch.setattr(auth_routes, "solicitar_recuperacao_senha", solicitar_recuperacao_falso)

    client = criar_client()
    resposta = client.post(
        "/auth/solicitar-recuperacao-senha",
        json={"email": "maria@example.com"},
    )

    assert resposta.status_code == 503
    assert resposta.json() == {
        "detail": "Nao foi possivel enviar o email de recuperacao agora. Tente novamente mais tarde."
    }
