from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import HistoricoFuncional


def criar_historico(db: Session, historico: HistoricoFuncional) -> HistoricoFuncional:
    db.add(historico)
    db.commit()
    db.refresh(historico)
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
