from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


def run_server() -> None:
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("UVICORN_RELOAD", "true").lower() in {"1", "true", "yes", "sim"}
    uvicorn.run("backend.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run_server()
