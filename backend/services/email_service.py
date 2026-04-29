from __future__ import annotations

import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from backend.config import (
    EMAIL_CONFIRMATION_SUBJECT,
    EMAIL_RECOVERY_SUBJECT,
    FRONTEND_BASE_URL,
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_USE_SSL,
    SMTP_USE_TLS,
)


def _validar_configuracao_smtp() -> None:
    if not SMTP_HOST:
        raise RuntimeError(
            "Configure SMTP_HOST, SMTP_PORT e as credenciais de envio para mandar emails."
        )


def _montar_envio_email(destinatario: str, assunto: str, texto: str, html: str) -> EmailMessage:
    mensagem = EmailMessage()
    remetente_email = SMTP_FROM_EMAIL or SMTP_USERNAME or "no-reply@localhost"
    remetente_nome = SMTP_FROM_NAME or "Gestao de Carreira"

    mensagem["Subject"] = assunto
    mensagem["From"] = formataddr((remetente_nome, remetente_email))
    mensagem["To"] = destinatario
    mensagem.set_content(texto)
    mensagem.add_alternative(html, subtype="html")
    return mensagem


def _enviar_mensagem(mensagem: EmailMessage) -> None:
    _validar_configuracao_smtp()

    cliente_cls = smtplib.SMTP_SSL if SMTP_USE_SSL else smtplib.SMTP
    try:
        with cliente_cls(SMTP_HOST, SMTP_PORT, timeout=30) as cliente:
            cliente.ehlo()
            if SMTP_USE_TLS and not SMTP_USE_SSL:
                cliente.starttls()
                cliente.ehlo()

            if SMTP_USERNAME:
                cliente.login(SMTP_USERNAME, SMTP_PASSWORD)

            cliente.send_message(mensagem)
    except OSError as erro:
        raise RuntimeError("Nao foi possivel conectar ao servidor de email SMTP.") from erro
    except smtplib.SMTPException as erro:
        raise RuntimeError("Nao foi possivel enviar o email pelo servidor SMTP.") from erro


def _montar_link_confirmacao(token: str) -> str:
    return f"{FRONTEND_BASE_URL}/confirmar-email?token={token}"


def _montar_link_redefinicao(token: str) -> str:
    return f"{FRONTEND_BASE_URL}/redefinir-senha?token={token}"


def enviar_email_confirmacao(destinatario: str, nome: str, token: str) -> None:
    link = _montar_link_confirmacao(token)
    texto = "\n".join(
        [
            f"Ola, {nome}.",
            "",
            "Confirme seu cadastro clicando no link abaixo:",
            link,
            "",
            "Se voce nao solicitou este cadastro, pode ignorar esta mensagem.",
        ]
    )
    html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #111827;">
            <p>Ola, {nome}.</p>
            <p>Confirme seu cadastro clicando no link abaixo:</p>
            <p><a href="{link}">{link}</a></p>
            <p>Se voce nao solicitou este cadastro, pode ignorar esta mensagem.</p>
          </body>
        </html>
    """
    mensagem = _montar_envio_email(
        destinatario=destinatario,
        assunto=EMAIL_CONFIRMATION_SUBJECT,
        texto=texto,
        html=html,
    )
    _enviar_mensagem(mensagem)


def enviar_email_recuperacao_senha(destinatario: str, nome: str, token: str) -> None:
    link = _montar_link_redefinicao(token)
    texto = "\n".join(
        [
            f"Ola, {nome}.",
            "",
            "Recebemos uma solicitacao para redefinir sua senha.",
            "Clique no link abaixo para definir uma nova senha:",
            link,
            "",
            "Se voce nao solicitou isso, pode ignorar esta mensagem.",
        ]
    )
    html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #111827;">
            <p>Ola, {nome}.</p>
            <p>Recebemos uma solicitacao para redefinir sua senha.</p>
            <p>Clique no link abaixo para definir uma nova senha:</p>
            <p><a href="{link}">{link}</a></p>
            <p>Se voce nao solicitou isso, pode ignorar esta mensagem.</p>
          </body>
        </html>
    """
    mensagem = _montar_envio_email(
        destinatario=destinatario,
        assunto=EMAIL_RECOVERY_SUBJECT,
        texto=texto,
        html=html,
    )
    _enviar_mensagem(mensagem)
