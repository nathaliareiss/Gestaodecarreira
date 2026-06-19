from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.env_loader import ambiente_efetivo, carregar_primeiro_env, deve_sobrescrever_env


ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def _bool_label(valor: bool) -> str:
    return "sim" if valor else "nao"


def _mascarar_origem_provavel(tinha_env_processo: bool, env_file: Path | None, override: bool) -> str:
    if tinha_env_processo and not override:
        return "variavel de ambiente do processo/sistema"

    if env_file and env_file.is_file():
        return str(env_file.resolve())

    if tinha_env_processo:
        return "variavel de ambiente do processo/sistema"

    return "nao encontrada"


def _valor_no_arquivo(path: Path, chave: str) -> str:
    if not path.is_file():
        return ""
    valor = dotenv_values(path).get(chave)
    return str(valor or "").strip()


def main() -> None:
    valor_processo_antes = os.environ.get("DATABASE_URL", "").strip()
    env_file_database_url = _valor_no_arquivo(ENV_FILE, "DATABASE_URL")
    env_file_environment = ambiente_efetivo(ENV_FILE)
    override_planejado = deve_sobrescrever_env(ENV_FILE)

    resultado = carregar_primeiro_env((ENV_FILE,))
    database_url = os.environ.get("DATABASE_URL", "").strip()
    partes = urlparse(database_url) if database_url else None
    host = partes.hostname if partes else None
    porta = partes.port if partes else None
    banco = (partes.path.lstrip("/") or None) if partes else None
    parece_supabase = bool(host and ("supabase.co" in host or "supabase.com" in host))
    origem_provavel = _mascarar_origem_provavel(
        bool(valor_processo_antes),
        resultado.path,
        resultado.override,
    )

    print("Diagnostico da DATABASE_URL")
    print(f"DATABASE_URL definida: {_bool_label(bool(database_url))}")
    print(f"Host: {host or '-'}")
    print(f"Porta: {porta or '-'}")
    print(f"Banco: {banco or '-'}")
    print(f"Parece Supabase: {_bool_label(parece_supabase)}")
    print(f"Arquivo .env usado: {str(resultado.path.resolve()) if resultado.path else '-'}")
    print(f"ENVIRONMENT/APP_ENV efetivo: {env_file_environment or '-'}")
    print(f"Override do .env ativo: {_bool_label(resultado.override)}")
    print(f"Origem provavel da DATABASE_URL efetiva: {origem_provavel}")
    print(f"DATABASE_URL existia no processo antes do .env: {_bool_label(bool(valor_processo_antes))}")
    print(f"DATABASE_URL existe em backend/.env: {_bool_label(bool(env_file_database_url))}")
    print(f"Override seria ativado para backend/.env: {_bool_label(override_planejado)}")


if __name__ == "__main__":
    main()
