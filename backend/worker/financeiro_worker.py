from __future__ import annotations

from rq import Worker

from backend.logger import logger
from backend.queue.queue_config import obter_conexao_redis


def executar_worker_financeiro() -> None:
    conexao = obter_conexao_redis()
    if conexao is None:
        raise RuntimeError(
            "Nao foi possivel iniciar o worker financeiro porque o Redis nao esta configurado ou indisponivel."
        )

    logger.info(
        "Iniciando worker financeiro",
        extra={"filas": ["financeiro"]},
    )
    worker = Worker(["financeiro"], connection=conexao)
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    executar_worker_financeiro()
