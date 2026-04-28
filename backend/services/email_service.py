from __future__ import annotations

import base64
from email.message import EmailMessage
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ModuleNotFoundError as import_error:  # pragma: no cover - fallback de ambiente
    Request = None  # type: ignore[assignment]
    Credentials = None  # type: ignore[assignment]
    InstalledAppFlow = None  # type: ignore[assignment]
    build = None  # type: ignore[assignment]
    HttpError = None  # type: ignore[assignment]
    _GOOGLE_IMPORT_ERROR = import_error
else:
    _GOOGLE_IMPORT_ERROR = None

from backend.config import (
    EMAIL_CONFIRMATION_SUBJECT,
    FRONTEND_BASE_URL,
    GOOGLE_GMAIL_CLIENT_FILE,
    GOOGLE_GMAIL_SCOPES,
    GOOGLE_GMAIL_TOKEN_FILE,
)


def _montar_link_confirmacao(token: str) -> str:
    return f"{FRONTEND_BASE_URL}/confirmar-email?token={token}"


def _garantir_dependencias_gmail() -> None:
    if _GOOGLE_IMPORT_ERROR is not None:
        raise RuntimeError(
            "As dependencias do Gmail API nao estao instaladas. "
            "Rode `pip install .` ou `pip install google-api-python-client "
            "google-auth-httplib2 google-auth-oauthlib`."
        ) from _GOOGLE_IMPORT_ERROR


def _montar_corpo_email(nome: str, link: str) -> EmailMessage:
    mensagem = EmailMessage()
    mensagem["Subject"] = EMAIL_CONFIRMATION_SUBJECT
    mensagem.set_content(
        "\n".join(
            [
                f"Ola, {nome}.",
                "",
                "Confirme seu cadastro clicando no link abaixo:",
                link,
                "",
                "Se voce nao solicitou esse cadastro, pode ignorar esta mensagem.",
            ]
        )
    )
    mensagem.add_alternative(
        f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #111827;">
            <p>Ola, {nome}.</p>
            <p>Confirme seu cadastro clicando no link abaixo:</p>
            <p><a href="{link}">{link}</a></p>
            <p>Se voce nao solicitou esse cadastro, pode ignorar esta mensagem.</p>
          </body>
        </html>
        """,
        subtype="html",
    )
    return mensagem


def _garantir_arquivo_client_secret() -> Path:
    _garantir_dependencias_gmail()
    if not GOOGLE_GMAIL_CLIENT_FILE.exists():
        raise RuntimeError(
            "Arquivo de credenciais do Google nao encontrado. "
            "Coloque o JSON do OAuth em backend/ ou defina GOOGLE_GMAIL_CLIENT_FILE."
        )
    return GOOGLE_GMAIL_CLIENT_FILE


def _garantir_credenciais_autorizadas() -> Credentials:
    _garantir_dependencias_gmail()
    if not GOOGLE_GMAIL_TOKEN_FILE.exists():
        raise RuntimeError(
            "Token do Gmail nao encontrado. "
            "Execute `python -m backend.scripts.google_gmail_auth` uma vez para gerar o arquivo."
        )

    credenciais = Credentials.from_authorized_user_file(
        str(GOOGLE_GMAIL_TOKEN_FILE),
        scopes=list(GOOGLE_GMAIL_SCOPES),
    )

    if credenciais.valid:
        return credenciais

    if credenciais.expired and credenciais.refresh_token:
        credenciais.refresh(Request())
        GOOGLE_GMAIL_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        GOOGLE_GMAIL_TOKEN_FILE.write_text(credenciais.to_json(), encoding="utf-8")
        return credenciais

    raise RuntimeError(
        "Credenciais do Gmail expiraram ou ficaram incompletas. "
        "Execute novamente `python -m backend.scripts.google_gmail_auth`."
    )


def autorizar_gmail_interativamente() -> Path:
    _garantir_dependencias_gmail()
    client_file = _garantir_arquivo_client_secret()
    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_file),
        scopes=list(GOOGLE_GMAIL_SCOPES),
    )
    credenciais = flow.run_local_server(port=0)
    GOOGLE_GMAIL_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    GOOGLE_GMAIL_TOKEN_FILE.write_text(credenciais.to_json(), encoding="utf-8")
    return GOOGLE_GMAIL_TOKEN_FILE


def _obter_remetente(service) -> str:
    perfil = service.users().getProfile(userId="me").execute()
    email_remetente = perfil.get("emailAddress")
    if not email_remetente:
        raise RuntimeError("Nao foi possivel descobrir o endereco do remetente do Gmail.")
    return email_remetente


def enviar_email_confirmacao(destinatario: str, nome: str, token: str) -> None:
    _garantir_dependencias_gmail()
    credenciais = _garantir_credenciais_autorizadas()
    service = build("gmail", "v1", credentials=credenciais, cache_discovery=False)
    remetente = _obter_remetente(service)

    link = _montar_link_confirmacao(token)
    mensagem = _montar_corpo_email(nome, link)
    mensagem["From"] = remetente
    mensagem["To"] = destinatario

    raw = base64.urlsafe_b64encode(mensagem.as_bytes()).decode("utf-8")

    try:
        service.users().messages().send(
            userId="me",
            body={"raw": raw},
        ).execute()
    except HttpError as erro:
        raise RuntimeError(
            "Nao foi possivel enviar o email de confirmacao pelo Gmail."
        ) from erro
