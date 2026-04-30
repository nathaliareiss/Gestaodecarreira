from __future__ import annotations

import json
import logging
import os

BASE_LOG_RECORD_KEYS = set(
    logging.LogRecord(
        name="app",
        level=logging.INFO,
        pathname=__file__,
        lineno=0,
        msg="",
        args=(),
        exc_info=None,
    ).__dict__.keys()
)
BASE_LOG_RECORD_KEYS.update({"message", "asctime", "exc_text"})


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        mensagem_formatada = super().format(record)
        extras = self._formatar_extras(record)
        if extras:
            return f"{mensagem_formatada} | {extras}"
        return mensagem_formatada

    def _formatar_extras(self, record: logging.LogRecord) -> str:
        partes: list[str] = []
        for chave, valor in record.__dict__.items():
            if chave in BASE_LOG_RECORD_KEYS or chave.startswith("_"):
                continue

            if isinstance(valor, str):
                valor_formatado = valor
            elif isinstance(valor, (int, float, bool)) or valor is None:
                valor_formatado = str(valor)
            else:
                valor_formatado = json.dumps(valor, ensure_ascii=False, default=str)

            partes.append(f"{chave}={valor_formatado}")
        return " ".join(partes)


def _ler_nivel_log() -> int:
    nome_nivel = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    return getattr(logging, nome_nivel, logging.INFO)


logger = logging.getLogger("app")
logger.setLevel(_ler_nivel_log())
logger.propagate = False

if not logger.handlers:
    formatter = StructuredFormatter("%(asctime)s | %(levelname)s | %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
