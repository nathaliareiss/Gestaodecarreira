from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from backend.database.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    apelido = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    login = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    token_confirmacao_email = Column(String, unique=True, nullable=False)
    email_confirmado = Column(Boolean, nullable=False, default=False)
    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    confirmado_em = Column(DateTime(timezone=True), nullable=True)

    @property
    def senha_cadastrada(self) -> bool:
        return bool(self.senha_hash)
