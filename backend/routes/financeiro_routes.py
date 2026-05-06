from __future__ import annotations

import os
import tempfile
from decimal import Decimal

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.services.contracheque_parser import parse_contracheque

router = APIRouter(prefix="/financeiro", tags=["financeiro"])


def _serializar_valor(valor):
    if isinstance(valor, Decimal):
        return format(valor, "f")

    return valor


def _serializar_contracheque(dados: dict[str, object]) -> dict[str, object]:
    return {chave: _serializar_valor(valor) for chave, valor in dados.items()}


@router.post("/contracheque/analisar")
async def analisar_contracheque(arquivo: UploadFile = File(...)) -> dict[str, object]:
    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel ler o arquivo enviado.",
        )

    if not conteudo.lstrip().startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie um arquivo PDF valido.",
        )

    caminho_temporario = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as arquivo_temporario:
            arquivo_temporario.write(conteudo)
            caminho_temporario = arquivo_temporario.name

        dados = parse_contracheque(caminho_temporario)
        return _serializar_contracheque(dados)
    except HTTPException:
        raise
    except Exception as erro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nao foi possivel analisar o contracheque. Verifique o PDF e tente novamente.",
        ) from erro
    finally:
        if caminho_temporario:
            try:
                os.unlink(caminho_temporario)
            except FileNotFoundError:
                pass
