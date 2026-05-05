"""Entrada do servidor FastAPI do projeto."""

from backend.config import HOST, PORT
from backend.logger import logger


def run_server() -> None:
    import uvicorn
    from backend.app import app

    logger.info("Iniciando servidor local", extra={"host": HOST, "port": PORT})
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    run_server()
