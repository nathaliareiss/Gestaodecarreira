from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.cache.redis_cache import (
    chave_historico_ultimo_usuario,
    invalidar_cache,
)
from backend.database.models import HistoricoFuncional


def criar_historico(db: Session, historico: HistoricoFuncional) -> HistoricoFuncional:
    db.add(historico)
    db.commit()
    db.refresh(historico)
    if historico.usuario_id is not None:
        invalidar_cache(chave_historico_ultimo_usuario(historico.usuario_id))
    return historico


def obter_ultimo_historico_por_usuario(
    db: Session,
    usuario_id: int,
) -> HistoricoFuncional | None:
    stmt = (
        select(HistoricoFuncional)
        .where(HistoricoFuncional.usuario_id == usuario_id)
        .order_by(HistoricoFuncional.criado_em.desc(), HistoricoFuncional.id.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def listar_historicos_por_usuario(
    db: Session,
    usuario_id: int,
) -> list[HistoricoFuncional]:
    stmt = select(HistoricoFuncional).where(HistoricoFuncional.usuario_id == usuario_id)
    return list(db.scalars(stmt).all())


def remover_historicos_por_usuario(db: Session, usuario_id: int) -> int:
    historicos = listar_historicos_por_usuario(db, usuario_id)
    total = len(historicos)
    db.execute(delete(HistoricoFuncional).where(HistoricoFuncional.usuario_id == usuario_id))
    db.commit()
    invalidar_cache(chave_historico_ultimo_usuario(usuario_id))
    return total
