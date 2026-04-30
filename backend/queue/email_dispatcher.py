from __future__ import annotations

from backend.logger import logger
from backend.queue.queue_config import obter_fila_emails
from backend.queue.tasks.email_tasks import (
    enviar_email_confirmacao_job,
    enviar_email_recuperacao_senha_job,
)
from backend.services.email_service import (
    enviar_email_confirmacao,
    enviar_email_recuperacao_senha,
)


def agendar_email_confirmacao(destinatario: str, nome: str, token: str) -> None:
    fila = obter_fila_emails()
    if fila is None:
        logger.warning(
            "Fila de emails indisponivel, enviando confirmacao de forma direta",
            extra={"destinatario": destinatario, "tipo": "confirmacao"},
        )
        enviar_email_confirmacao(destinatario=destinatario, nome=nome, token=token)
        return

    job = fila.enqueue(
        enviar_email_confirmacao_job,
        destinatario,
        nome,
        token,
    )
    logger.info(
        "Email de confirmacao agendado",
        extra={"destinatario": destinatario, "job_id": job.id},
    )


def agendar_email_recuperacao_senha(destinatario: str, nome: str, token: str) -> None:
    fila = obter_fila_emails()
    if fila is None:
        logger.warning(
            "Fila de emails indisponivel, enviando recuperacao de forma direta",
            extra={"destinatario": destinatario, "tipo": "recuperacao_senha"},
        )
        enviar_email_recuperacao_senha(destinatario=destinatario, nome=nome, token=token)
        return

    job = fila.enqueue(
        enviar_email_recuperacao_senha_job,
        destinatario,
        nome,
        token,
    )
    logger.info(
        "Email de recuperacao agendado",
        extra={"destinatario": destinatario, "job_id": job.id},
    )
