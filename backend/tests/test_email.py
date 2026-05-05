"""Teste manual opcional para validacao de SMTP.

Este modulo nao executa envio real automaticamente, porque isso causava emails
indesejados durante `unittest discover` e importacoes indiretas.

Para rodar manualmente, defina:
    RUN_REAL_SMTP_TEST=1
e execute este arquivo diretamente.
"""

from __future__ import annotations

import os
import smtplib
from email.mime.text import MIMEText

from backend.logger import logger


def main() -> None:
    if os.getenv("RUN_REAL_SMTP_TEST") != "1":
        logger.info(
            "Teste SMTP manual desativado",
            extra={"dica": "defina RUN_REAL_SMTP_TEST=1 para enviar um email de teste"},
        )
        return

    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_password:
        raise RuntimeError("Configure SMTP_USER e SMTP_PASSWORD para testar o envio.")

    msg = MIMEText("Teste de envio de email", "plain")
    msg["Subject"] = "Teste SMTP"
    msg["From"] = smtp_user
    msg["To"] = smtp_user

    logger.info(
        "Configuracao SMTP carregada",
        extra={
            "smtp_user": smtp_user,
            "tem_senha": bool(smtp_password),
            "tamanho_senha": len(smtp_password),
        },
    )

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info("Email enviado com sucesso", extra={"destinatario": smtp_user})
    except Exception:
        logger.exception("Erro ao enviar email")
        raise


if __name__ == "__main__":
    main()
