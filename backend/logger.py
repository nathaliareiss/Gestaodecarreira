from __future__ import annotations

import json
import logging
import os
import re

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

SENSITIVE_EXACT_KEYS = {
    "arquivo_nome",
    "arquivo_storage_path",
    "afastamentos_storage_path",
    "cpf",
    "destinatario",
    "email",
    "file_hash",
    "identificador",
    "link_final",
    "local_path",
    "login",
    "matricula",
    "masp",
    "nome",
    "storage_path",
}
SENSITIVE_KEY_FRAGMENTS = ("token", "senha")
EMAIL_PATTERN = re.compile(r"\b([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
CPF_PATTERN = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
LONG_SECRET_PATTERN = re.compile(r"\b[a-f0-9]{24,}\b", re.IGNORECASE)


def _mascarar_email(valor: str) -> str:
    return EMAIL_PATTERN.sub(lambda match: f"{match.group(1)}***@{match.group(2)}", valor)


def _mascarar_cpf(valor: str) -> str:
    return CPF_PATTERN.sub("***.***.***-**", valor)


def _mascarar_segredo(valor: str) -> str:
    return LONG_SECRET_PATTERN.sub("[redacted-secret]", valor)


def _sanitizar_texto(valor: str) -> str:
    return _mascarar_segredo(_mascarar_cpf(_mascarar_email(valor)))


def _chave_sensivel(chave: str) -> bool:
    chave_normalizada = chave.strip().lower()
    if chave_normalizada in SENSITIVE_EXACT_KEYS:
        return True
    return any(fragmento in chave_normalizada for fragmento in SENSITIVE_KEY_FRAGMENTS)


def _mascarar_valor_por_chave(chave: str, valor: object) -> object:
    if isinstance(valor, dict):
        return {
            chave_interna: _mascarar_valor_por_chave(chave_interna, valor_interno)
            for chave_interna, valor_interno in valor.items()
        }

    if isinstance(valor, list):
        return [_mascarar_valor_por_chave(chave, item) for item in valor]

    if isinstance(valor, tuple):
        return tuple(_mascarar_valor_por_chave(chave, item) for item in valor)

    if isinstance(valor, str):
        if _chave_sensivel(chave):
            if "email" in chave or chave == "destinatario":
                return _mascarar_email(valor)
            if chave == "cpf":
                return "***.***.***-**"
            if "arquivo" in chave or "path" in chave:
                return "[redacted-file]"
            if "token" in chave or "senha" in chave or chave == "file_hash":
                return "[redacted-secret]"
            return "[redacted]"
        return _sanitizar_texto(valor)

    return valor


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

            valor = _mascarar_valor_por_chave(chave, valor)

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
