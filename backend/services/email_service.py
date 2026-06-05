from __future__ import annotations

import smtplib
from html import escape
from email.message import EmailMessage
from email.utils import formataddr
from time import perf_counter

import requests

from backend.logger import logger
from backend.metrics import registrar_envio_email
from backend.config import (
    EMAIL_PROVIDER,
    EMAIL_CONFIRMATION_SUBJECT,
    EMAIL_RECOVERY_SUBJECT,
    FRONTEND_BASE_URL,
    SMTP_FROM,
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_TIMEOUT,
    RESEND_API_KEY,
    RESEND_FROM_EMAIL,
    SMTP_USER,
    SMTP_USE_SSL,
    SMTP_USE_TLS,
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
    remetente_email = RESEND_FROM_EMAIL or SMTP_FROM_EMAIL or SMTP_FROM or SMTP_USER or "no-reply@localhost"
    remetente_nome = SMTP_FROM_NAME or "Career Flow"

    mensagem["Subject"] = assunto
    mensagem["From"] = formataddr((remetente_nome, remetente_email))
    mensagem["To"] = destinatario
    mensagem.set_content(texto)
    mensagem.add_alternative(html, subtype="html")
    return mensagem


def _enviar_via_smtp(mensagem: EmailMessage) -> None:
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
            extra={
                "destinatario": mensagem["To"],
                "host": SMTP_HOST,
                "erro_tipo": type(erro).__name__,
            },
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
            extra={
                "destinatario": mensagem["To"],
                "host": SMTP_HOST,
                "porta": SMTP_PORT,
                "erro_tipo": type(erro).__name__,
            },
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
            extra={
                "destinatario": mensagem["To"],
                "host": SMTP_HOST,
                "erro_tipo": type(erro).__name__,
            },
        )
        registrar_envio_email(
            "smtp",
            "smtp_error",
            perf_counter() - inicio,
        )
        raise RuntimeError("Nao foi possivel enviar o email pelo servidor SMTP.") from erro


def _enviar_via_resend(mensagem: EmailMessage) -> None:
    if not RESEND_API_KEY:
        raise RuntimeError("Configure RESEND_API_KEY e RESEND_FROM_EMAIL para enviar emails via Resend.")

    if not mensagem.is_multipart():
        raise RuntimeError("Mensagem de email invalida para Resend.")

    texto = mensagem.get_body(preferencelist=("plain",))
    html = mensagem.get_body(preferencelist=("html",))
    inicio = perf_counter()
    payload = {
        "from": mensagem["From"],
        "to": [mensagem["To"]],
        "subject": mensagem["Subject"],
        "text": texto.get_content() if texto else "",
        "html": html.get_content() if html else "",
    }

    try:
        logger.info(
            "Enviando email via Resend",
            extra={"destinatario": mensagem["To"]},
        )
        resposta = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=SMTP_TIMEOUT,
        )
        if resposta.status_code >= 400:
            raise RuntimeError(f"Resend recusou o envio ({resposta.status_code}).")

        logger.info("Email enviado com sucesso", extra={"destinatario": mensagem["To"]})
        registrar_envio_email("resend", "sent", perf_counter() - inicio)
    except requests.RequestException as erro:
        logger.error(
            "Falha ao enviar email via Resend",
            extra={"destinatario": mensagem["To"], "erro_tipo": type(erro).__name__},
        )
        registrar_envio_email("resend", "connection_error", perf_counter() - inicio)
        raise RuntimeError("Nao foi possivel enviar o email via Resend.") from erro
    except RuntimeError:
        registrar_envio_email("resend", "provider_error", perf_counter() - inicio)
        raise


def _enviar_mensagem(mensagem: EmailMessage) -> None:
    provedor = EMAIL_PROVIDER or ("resend" if RESEND_API_KEY else "smtp")
    if provedor == "resend":
        try:
            _enviar_via_resend(mensagem)
            return
        except Exception as erro:
            logger.warning(
                "Resend falhou, tentando SMTP como fallback",
                extra={
                    "destinatario": mensagem["To"],
                    "erro": str(erro),
                    "erro_tipo": type(erro).__name__,
                },
            )
            if SMTP_HOST:
                _enviar_via_smtp(mensagem)
            else:
                raise
            return

    try:
        _enviar_via_smtp(mensagem)
    except Exception as erro:
        if RESEND_API_KEY:
            logger.warning(
                "SMTP falhou, tentando Resend como fallback",
                extra={
                    "destinatario": mensagem["To"],
                    "erro": str(erro),
                    "erro_tipo": type(erro).__name__,
                },
            )
            _enviar_via_resend(mensagem)
            return
        raise


def _montar_link_confirmacao(token: str) -> str:
    return f"{FRONTEND_BASE_URL}/confirmar-email?token={token}"


def _montar_link_redefinicao(token: str) -> str:
    return f"{FRONTEND_BASE_URL}/definir-senha?token={token}"


def _montar_template_email_acao(
    titulo: str,
    saudacao: str,
    descricao: str,
    botao_texto: str,
    link: str,
    link_texto: str,
    aviso: str,
) -> tuple[str, str]:
    link_escapado = escape(link, quote=True)
    titulo_escapado = escape(titulo)
    saudacao_escapada = escape(saudacao)
    descricao_escapada = escape(descricao)
    botao_escapado = escape(botao_texto)
    aviso_escapado = escape(aviso)
    link_texto_escapado = escape(link_texto)

    texto = "\n".join(
        [
            saudacao,
            "",
            descricao,
            link,
            "",
            aviso,
        ]
    )
    html = f"""
        <html>
          <body style="margin:0;padding:0;background:#f1f8f8;font-family:Arial,Helvetica,sans-serif;color:#0f172a;">
            <div style="padding:32px 16px;">
              <div style="max-width:620px;margin:0 auto;background:#ffffff;border:1px solid #d9ece8;border-radius:24px;overflow:hidden;box-shadow:0 18px 50px rgba(15,118,110,0.12);">
                <div style="background:linear-gradient(135deg,#0f766e 0%,#14b8a6 100%);padding:28px 32px;color:#ffffff;">
                  <div style="font-size:12px;letter-spacing:.22em;text-transform:uppercase;opacity:.9;margin-bottom:10px;">Career Flow</div>
                  <h1 style="margin:0;font-size:30px;line-height:1.1;">{titulo_escapado}</h1>
                </div>
                <div style="padding:32px;">
                  <p style="margin:0 0 16px;font-size:16px;line-height:1.7;color:#0f172a;">{saudacao_escapada}</p>
                  <p style="margin:0 0 28px;font-size:15px;line-height:1.7;color:#334155;">{descricao_escapada}</p>
                  <div style="margin:0 0 28px;">
                    <a href="{link_escapado}" style="display:inline-block;background:#0f766e;color:#ffffff;text-decoration:none;padding:14px 22px;border-radius:999px;font-weight:700;box-shadow:0 10px 24px rgba(15,118,110,0.2);">{botao_escapado}</a>
                  </div>
                  <p style="margin:0 0 10px;font-size:13px;line-height:1.6;color:#64748b;">Se o botão não funcionar, copie e cole este link no navegador:</p>
                  <p style="margin:0 0 28px;font-size:13px;line-height:1.6;word-break:break-word;">
                    <a href="{link_escapado}" style="color:#0f766e;">{link_texto_escapado}</a>
                  </p>
                  <p style="margin:0;font-size:13px;line-height:1.6;color:#64748b;">{aviso_escapado}</p>
                </div>
              </div>
            </div>
          </body>
        </html>
    """
    return texto, html


def enviar_email_confirmacao(destinatario: str, nome: str, token: str) -> None:
    link = _montar_link_confirmacao(token)
    logger.info(
        "Preparando email de confirmacao",
        extra={"destinatario": destinatario, "tipo": "confirmacao"},
    )
    texto, html = _montar_template_email_acao(
        titulo="Confirme seu cadastro",
        saudacao=f"Ola, {nome}.",
        descricao="Clique no botão abaixo para confirmar seu cadastro no Career Flow e ativar seu acesso.",
        botao_texto="Clique para confirmar seu cadastro",
        link=link,
        link_texto=link,
        aviso="Se você não solicitou este cadastro, ignore este email.",
    )
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
    texto, html = _montar_template_email_acao(
        titulo="Redefina sua senha",
        saudacao=f"Ola, {nome}.",
        descricao="Recebemos uma solicitação para redefinir sua senha no Career Flow. Use o botão abaixo para criar uma nova senha com segurança.",
        botao_texto="Criar nova senha",
        link=link,
        link_texto=link,
        aviso="Se você não solicitou isso, ignore este email.",
    )
    mensagem = _montar_envio_email(
        destinatario=destinatario,
        assunto=EMAIL_RECOVERY_SUBJECT,
        texto=texto,
        html=html,
    )
    _enviar_mensagem(mensagem)
