from __future__ import annotations

from rq import Connection, Worker

from backend.logger import logger
from backend.queue.queue_config import obter_conexao_redis


def executar_worker() -> None:
    conexao = obter_conexao_redis()
    if conexao is None:
        raise RuntimeError(
            "Nao foi possivel iniciar o worker porque o Redis nao esta configurado ou indisponivel."
        )

    logger.info(
        "Iniciando worker da fila",
        extra={"filas": ["historicos", "financeiro"]},
    )
    with Connection(conexao):
        worker = Worker(["historicos", "financeiro"])
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    executar_worker()
