from __future__ import annotations

from time import perf_counter

from backend.logger import logger
from backend.metrics import registrar_envio_email
from backend.services.email_service import (
    enviar_email_confirmacao,
    enviar_email_recuperacao_senha,
)


def enviar_email_confirmacao_job(destinatario: str, nome: str, token: str) -> None:
    inicio = perf_counter()
    status = "sent"
    logger.info(
        "Worker enviando email de confirmacao",
        extra={"destinatario": destinatario, "tipo": "confirmacao"},
    )
    try:
        enviar_email_confirmacao(destinatario=destinatario, nome=nome, token=token)
    except Exception:
        status = "failed"
        raise
    finally:
        registrar_envio_email("confirmacao", status, perf_counter() - inicio)


def enviar_email_recuperacao_senha_job(destinatario: str, nome: str, token: str) -> None:
    inicio = perf_counter()
    status = "sent"
    logger.info(
        "Worker enviando email de recuperacao de senha",
        extra={"destinatario": destinatario, "tipo": "recuperacao_senha"},
    )
    try:
        enviar_email_recuperacao_senha(destinatario=destinatario, nome=nome, token=token)
    except Exception:
        status = "failed"
        raise
    finally:
        registrar_envio_email("recuperacao_senha", status, perf_counter() - inicio)
