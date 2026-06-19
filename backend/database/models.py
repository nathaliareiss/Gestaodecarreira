from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.database.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        Index("ix_usuarios_sessao_token_hash", "sessao_token_hash"),
        Index("ix_usuarios_redefinir_senha_token_hash", "redefinir_senha_token_hash"),
    )

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
    politica_privacidade_aceita_em = Column(DateTime(timezone=True), nullable=True)
    politica_privacidade_versao = Column(String, nullable=True)
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
    ferias_storage_path = Column(String, nullable=True)
    texto_extraido = Column(Text, nullable=False)
    dados_json = Column(Text, nullable=False)
    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_historicos_funcionais_usuario_criado_em_id", "usuario_id", "criado_em", "id"),
    )


class PayrollBatch(Base):
    __tablename__ = "payroll_batches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    total_files = Column(Integer, nullable=False, default=0)
    processed_files = Column(Integer, nullable=False, default=0)
    duplicated_files = Column(Integer, nullable=False, default=0)
    failed_files = Column(Integer, nullable=False, default=0)
    processing_seconds_total = Column(Numeric(14, 3, asdecimal=True), nullable=False, default=0)
    last_error_message = Column(String, nullable=False, default="")
    failure_messages = Column(Text, nullable=False, default="[]")
    missing_competencies = Column(Text, nullable=False, default="[]")
    status = Column(String, nullable=False, default="pending")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    paychecks = relationship(
        "Paycheck",
        back_populates="batch",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_payroll_batches_user_id_created_at", "user_id", "created_at"),
    )


class FinanceiroImportacaoTemporaria(Base):
    __tablename__ = "financeiro_importacoes_temporarias"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    scope = Column(String, nullable=False, default="financeiro_importacao")
    token_hash = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_financeiro_importacoes_temporarias_user_id_created_at", "user_id", "created_at", "id"),
    )


class SupportDocumentAccessGrant(Base):
    __tablename__ = "support_document_access_grants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    document_kind = Column(String, nullable=False, default="unknown")
    document_storage_path = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    granted_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_support_document_access_grants_user_id_created_at", "user_id", "created_at", "id"),
        Index("ix_support_document_access_grants_expires_at", "expires_at"),
    )


class WorkSchedule(Base):
    __tablename__ = "work_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    schedule_type = Column(String, nullable=False)
    anchor_date = Column(Date, nullable=False)
    state_code = Column(String, nullable=True)
    city_name = Column(String, nullable=True)
    working_weekdays_json = Column(Text, nullable=False, default="[]")
    custom_pattern_json = Column(Text, nullable=False, default="[]")
    note = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_work_schedules_user_id_is_active", "user_id", "is_active"),
        Index("ix_work_schedules_user_id_created_at", "user_id", "created_at"),
    )


class VacationPeriod(Base):
    __tablename__ = "vacation_periods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    title = Column(String, nullable=False, default="Ferias")
    vacation_type = Column(String, nullable=False, default="regular")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    requested_days = Column(Integer, nullable=True)
    counted_days = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_vacation_periods_user_id_start_date", "user_id", "start_date"),
        Index("ix_vacation_periods_user_id_end_date", "user_id", "end_date"),
    )


class WorkCalendarOverride(Base):
    __tablename__ = "work_calendar_overrides"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    override_date = Column(Date, nullable=False)
    is_working_day = Column(Boolean, nullable=False)
    title = Column(String, nullable=False, default="Excecao manual")
    note = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        Index("ix_work_calendar_overrides_user_id_override_date", "user_id", "override_date"),
    )


class Paycheck(Base):
    __tablename__ = "paychecks"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("payroll_batches.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    file_hash = Column(String, nullable=False, default="")
    matricula = Column(String, nullable=False, default="")
    competencia = Column(String, nullable=False)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    bruto = Column(Numeric(14, 2, asdecimal=True), nullable=False, default=0)
    descontos = Column(Numeric(14, 2, asdecimal=True), nullable=False, default=0)
    liquido = Column(Numeric(14, 2, asdecimal=True), nullable=False, default=0)
    vencimento_basico = Column(Numeric(14, 2, asdecimal=True), nullable=False, default=0)
    adicional_desempenho = Column(Numeric(14, 2, asdecimal=True), nullable=False, default=0)
    adicional_noturno = Column(Numeric(14, 2, asdecimal=True), nullable=False, default=0)
    irrf = Column(Numeric(14, 2, asdecimal=True), nullable=False, default=0)
    previdencia = Column(Numeric(14, 2, asdecimal=True), nullable=False, default=0)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    batch = relationship("PayrollBatch", back_populates="paychecks")
    items = relationship(
        "PaycheckItem",
        back_populates="paycheck",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_paychecks_batch_id_created_at", "batch_id", "created_at"),
        Index("ix_paychecks_user_id_ano_mes", "user_id", "ano", "mes"),
        Index("ix_paychecks_user_id_file_hash", "user_id", "file_hash"),
        Index("ix_paychecks_user_id_ano_mes_matricula", "user_id", "ano", "mes", "matricula"),
    )


class PaycheckItem(Base):
    __tablename__ = "paycheck_items"

    id = Column(Integer, primary_key=True, index=True)
    paycheck_id = Column(Integer, ForeignKey("paychecks.id"), nullable=False, index=True)
    tipo = Column(String, nullable=False)
    categoria_normalizada = Column(String, nullable=False, default="outros_vantagens")
    descricao_original = Column(String, nullable=False, default="")
    descricao = Column(String, nullable=False)
    valor = Column(Numeric(14, 2, asdecimal=True), nullable=False, default=0)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    paycheck = relationship("Paycheck", back_populates="items")

    __table_args__ = (
        Index("ix_paycheck_items_paycheck_id_tipo", "paycheck_id", "tipo"),
    )
