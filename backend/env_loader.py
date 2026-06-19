from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values, load_dotenv


DEVELOPMENT_ENVIRONMENTS = {"development", "dev", "local"}


@dataclass(frozen=True, slots=True)
class EnvLoadResult:
    path: Path | None
    override: bool
    environment: str


def _normalizar_ambiente(valor: str | None) -> str:
    return (valor or "").strip().lower()


def _ambiente_do_arquivo(path: Path) -> str:
    valores = dotenv_values(path)
    return _normalizar_ambiente(
        valores.get("ENVIRONMENT") or valores.get("APP_ENV") or None
    )


def ambiente_efetivo(path: Path | None) -> str:
    ambiente_processo = _normalizar_ambiente(os.getenv("ENVIRONMENT") or os.getenv("APP_ENV"))
    if ambiente_processo:
        return ambiente_processo

    if path and path.is_file():
        return _ambiente_do_arquivo(path)

    return ""


def deve_sobrescrever_env(path: Path | None) -> bool:
    return ambiente_efetivo(path) in DEVELOPMENT_ENVIRONMENTS


def carregar_primeiro_env(candidatos: tuple[Path, ...]) -> EnvLoadResult:
    for candidato in candidatos:
        if candidato.is_file():
            override = deve_sobrescrever_env(candidato)
            load_dotenv(candidato, override=override)
            return EnvLoadResult(
                path=candidato,
                override=override,
                environment=ambiente_efetivo(candidato),
            )

    return EnvLoadResult(
        path=None,
        override=deve_sobrescrever_env(None),
        environment=ambiente_efetivo(None),
    )
