from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import HOST, PORT
from backend.logger import logger

def run_server() -> None:
    import uvicorn
    from backend.app import app

    logger.info("Iniciando servidor local", extra={"host": HOST, "port": PORT})
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    run_server()
