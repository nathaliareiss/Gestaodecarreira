from __future__ import annotations

from backend.logger import logger
from backend.services.email_service import (
    enviar_email_confirmacao,
    enviar_email_recuperacao_senha,
)


def enviar_email_confirmacao_job(destinatario: str, nome: str, token: str) -> None:
    logger.info(
        "Worker enviando email de confirmacao",
        extra={"destinatario": destinatario, "tipo": "confirmacao"},
    )
    enviar_email_confirmacao(destinatario=destinatario, nome=nome, token=token)


def enviar_email_recuperacao_senha_job(destinatario: str, nome: str, token: str) -> None:
    logger.info(
        "Worker enviando email de recuperacao de senha",
        extra={"destinatario": destinatario, "tipo": "recuperacao_senha"},
    )
    enviar_email_recuperacao_senha(destinatario=destinatario, nome=nome, token=token)
