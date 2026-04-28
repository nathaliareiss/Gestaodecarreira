from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage

from backend.config import (
    EMAIL_CONFIRMATION_SUBJECT,
    FRONTEND_BASE_URL,
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USERNAME,
)


def _montar_link_confirmacao(token: str) -> str:
    return f"{FRONTEND_BASE_URL}/confirmar-email?token={token}"


def _validar_configuracao_smtp() -> None:
    if not SMTP_HOST:
        raise RuntimeError("SMTP_HOST nao configurado.")
    if not SMTP_FROM_EMAIL:
        raise RuntimeError("SMTP_FROM_EMAIL nao configurado.")
    if not SMTP_USERNAME:
        raise RuntimeError("SMTP_USERNAME nao configurado.")
    if not SMTP_PASSWORD:
        raise RuntimeError("SMTP_PASSWORD nao configurado.")


def enviar_email_confirmacao(destinatario: str, nome: str, token: str) -> None:
    _validar_configuracao_smtp()

    link = _montar_link_confirmacao(token)

    mensagem = EmailMessage()
    mensagem["Subject"] = EMAIL_CONFIRMATION_SUBJECT
    mensagem["From"] = SMTP_FROM_EMAIL
    mensagem["To"] = destinatario
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

    contexto = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as servidor:
        if SMTP_USE_TLS:
            servidor.starttls(context=contexto)
        servidor.login(SMTP_USERNAME, SMTP_PASSWORD)
        servidor.send_message(mensagem)
