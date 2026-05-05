from __future__ import annotations

import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from time import perf_counter

from backend.logger import logger
from backend.metrics import registrar_envio_email
from backend.config import (
    EMAIL_CONFIRMATION_SUBJECT,
    EMAIL_RECOVERY_SUBJECT,
    FRONTEND_BASE_URL,
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USER,
    SMTP_USE_SSL,
    SMTP_USE_TLS,
    SMTP_TIMEOUT,
)


def _validar_configuracao_smtp() -> None:
    if not SMTP_HOST:
        logger.critical(
            "Configuracao SMTP ausente",
            extra={"campo": "SMTP_HOST", "porta": SMTP_PORT},
        )
        raise RuntimeError(
            "Configure SMTP_HOST, SMTP_PORT e as credenciais de envio para mandar emails."
        )


def _montar_envio_email(destinatario: str, assunto: str, texto: str, html: str) -> EmailMessage:
    mensagem = EmailMessage()
    remetente_email = SMTP_FROM_EMAIL or SMTP_USER or "no-reply@localhost"
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
    inicio = perf_counter()
    try:
        logger.info(
            "Conectando ao SMTP",
            extra={
                "destinatario": mensagem["To"],
                "host": SMTP_HOST,
                "porta": SMTP_PORT,
                "tls": SMTP_USE_TLS,
                "ssl": SMTP_USE_SSL,
            },
        )
        with cliente_cls(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as cliente:
            cliente.ehlo()
            if SMTP_USE_TLS and not SMTP_USE_SSL:
                cliente.starttls()
                cliente.ehlo()

            if SMTP_USER:
                cliente.login(SMTP_USER, SMTP_PASSWORD)

            cliente.send_message(mensagem)
        logger.info("Email enviado com sucesso", extra={"destinatario": mensagem["To"]})
        registrar_envio_email(
            "smtp",
            "sent",
            perf_counter() - inicio,
        )
    except smtplib.SMTPAuthenticationError as erro:
        logger.error(
            "Credenciais SMTP recusadas",
            extra={"destinatario": mensagem["To"], "host": SMTP_HOST},
        )
        registrar_envio_email(
            "smtp",
            "auth_error",
            perf_counter() - inicio,
        )
        raise RuntimeError(
            "Credenciais SMTP recusadas. Verifique o SMTP_USER e a App Password do Gmail."
        ) from erro
    except OSError as erro:
        logger.error(
            "Falha ao conectar ao servidor SMTP",
            extra={"destinatario": mensagem["To"], "host": SMTP_HOST, "porta": SMTP_PORT},
        )
        registrar_envio_email(
            "smtp",
            "connection_error",
            perf_counter() - inicio,
        )
        raise RuntimeError("Nao foi possivel conectar ao servidor de email SMTP.") from erro
    except smtplib.SMTPException as erro:
        logger.error(
            "Falha ao enviar email pelo SMTP",
            extra={"destinatario": mensagem["To"], "host": SMTP_HOST},
        )
        registrar_envio_email(
            "smtp",
            "smtp_error",
            perf_counter() - inicio,
        )
        raise RuntimeError("Nao foi possivel enviar o email pelo servidor SMTP.") from erro


def _montar_link_confirmacao(token: str) -> str:
    return f"{FRONTEND_BASE_URL}/confirmar-email?token={token}"


def _montar_link_redefinicao(token: str) -> str:
    return f"{FRONTEND_BASE_URL}/redefinir-senha?token={token}"


def enviar_email_confirmacao(destinatario: str, nome: str, token: str) -> None:
    link = _montar_link_confirmacao(token)
    logger.info(
        "Preparando email de confirmacao",
        extra={"destinatario": destinatario, "tipo": "confirmacao"},
    )
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
    logger.info(
        "Preparando email de recuperacao de senha",
        extra={"destinatario": destinatario, "tipo": "recuperacao_senha"},
    )
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
