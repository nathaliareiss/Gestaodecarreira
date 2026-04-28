from __future__ import annotations

from sqlalchemy import desc
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
    return (
        db.query(HistoricoFuncional)
        .filter(HistoricoFuncional.usuario_id == usuario_id)
        .order_by(desc(HistoricoFuncional.criado_em), desc(HistoricoFuncional.id))
        .first()
    )

