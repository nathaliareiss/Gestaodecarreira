from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.database.models import FinanceiroImportacaoTemporaria, Usuario
from backend.database.database import ativar_acesso_backend
from backend.logger import logger
from backend.repositories.financeiro_repository import (
    criar_importacao_temporaria_financeira as criar_registro_importacao_temporaria_financeira,
    invalidar_importacoes_temporarias_ativas,
    obter_importacao_temporaria_ativa_por_token_hash,
    marcar_importacao_temporaria_como_usada,
)
from backend.services.security_service import gerar_hash_sha256, gerar_token_seguro

SCOPE_IMPORTACAO_FINANCEIRA = "financeiro_importacao"
TEMPO_VIDA_PADRAO_MINUTOS = 30


@dataclass(frozen=True)
class ImportacaoTemporariaGerada:
    token: str
    importacao: FinanceiroImportacaoTemporaria


def _hash_token(valor: str) -> str:
    return gerar_hash_sha256(valor)


def criar_importacao_temporaria_financeira(
    db: Session,
    usuario: Usuario,
    minutos_validade: int = TEMPO_VIDA_PADRAO_MINUTOS,
) -> ImportacaoTemporariaGerada:
    invalidar_importacoes_temporarias_ativas(db, usuario.id, SCOPE_IMPORTACAO_FINANCEIRA)

    token = gerar_token_seguro()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutos_validade)
    importacao = criar_registro_importacao_temporaria_financeira(
        db,
        user_id=usuario.id,
        token_hash=_hash_token(token),
        expires_at=expires_at,
        scope=SCOPE_IMPORTACAO_FINANCEIRA,
    )
    logger.info(
        "Importacao temporaria criada",
        extra={"usuario_id": usuario.id, "importacao_id": importacao.id},
    )
    return ImportacaoTemporariaGerada(token=token, importacao=importacao)


def validar_importacao_temporaria_financeira(
    db: Session,
    token: str,
) -> FinanceiroImportacaoTemporaria:
    ativar_acesso_backend(db)
    importacao = obter_importacao_temporaria_ativa_por_token_hash(db, _hash_token(token))
    if importacao is None or importacao.scope != SCOPE_IMPORTACAO_FINANCEIRA:
        raise ValueError("Token temporario invalido ou expirado.")

    return importacao


def usar_importacao_temporaria_financeira(
    db: Session,
    token: str,
) -> FinanceiroImportacaoTemporaria:
    ativar_acesso_backend(db)
    importacao = validar_importacao_temporaria_financeira(db, token)
    return marcar_importacao_temporaria_como_usada(db, importacao)
