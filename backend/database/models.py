from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text

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
    data_exercicio = Column(Date, nullable=True)
    sessao_token_hash = Column(String, nullable=True)
    sessao_expira_em = Column(DateTime(timezone=True), nullable=True)
    redefinir_senha_token_hash = Column(String, nullable=True)
    redefinir_senha_expira_em = Column(DateTime(timezone=True), nullable=True)
    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    confirmado_em = Column(DateTime(timezone=True), nullable=True)

    @property
    def senha_cadastrada(self) -> bool:
        return bool(self.senha_hash)


class HistoricoFuncional(Base):
    __tablename__ = "historicos_funcionais"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    arquivo_nome = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    masp = Column(String, nullable=False, index=True)
    cpf = Column(String, nullable=True)
    data_emissao = Column(Date, nullable=True)
    data_nascimento = Column(Date, nullable=False)
    data_posse = Column(Date, nullable=False)
    data_exercicio = Column(Date, nullable=False)
    cargo_atual = Column(String, nullable=False)
    simbolo_atual = Column(String, nullable=False)
    nivel_atual = Column(String, nullable=False)
    grau_atual = Column(String, nullable=False)
    tempo_clt_averbado_anos = Column(Integer, nullable=False, default=0)
    tempo_clt_creditado_anos = Column(Integer, nullable=False, default=0)
    arquivo_storage_path = Column(String, nullable=True)
    afastamentos_storage_path = Column(String, nullable=True)
    texto_extraido = Column(Text, nullable=False)
    dados_json = Column(Text, nullable=False)
    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
