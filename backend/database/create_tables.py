from sqlalchemy import text

from backend.config import SUPABASE_STORAGE_BUCKET, SUPABASE_STORAGE_CONFIGURED
from backend.database.database import Base, engine
from backend.database import models as database_models  # noqa: F401
from backend.logger import logger


def habilitar_rls_tabelas_publicas() -> None:
    current_user_id_sql = "NULLIF(current_setting('app.current_user_id', true), '')::INTEGER"
    comandos = [
        "ALTER TABLE IF EXISTS public.usuarios ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.usuarios FORCE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.historicos_funcionais ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.historicos_funcionais FORCE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.payroll_batches ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.payroll_batches FORCE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.financeiro_importacoes_temporarias ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.financeiro_importacoes_temporarias FORCE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.paychecks ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.paychecks FORCE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.paycheck_items ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.paycheck_items FORCE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.support_document_access_grants ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.support_document_access_grants FORCE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.work_schedules ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.work_schedules FORCE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.vacation_periods ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.vacation_periods FORCE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.work_calendar_overrides ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.work_calendar_overrides FORCE ROW LEVEL SECURITY",
        "DROP POLICY IF EXISTS usuarios_backend_access ON public.usuarios",
        "DROP POLICY IF EXISTS usuarios_self_access ON public.usuarios",
        "DROP POLICY IF EXISTS usuarios_self_update ON public.usuarios",
        "DROP POLICY IF EXISTS usuarios_self_delete ON public.usuarios",
        "CREATE POLICY usuarios_backend_access ON public.usuarios FOR ALL TO PUBLIC "
        "USING (current_setting('app.backend_access', true) = 'on') "
        "WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        f"CREATE POLICY usuarios_self_access ON public.usuarios FOR SELECT TO PUBLIC "
        f"USING (id = {current_user_id_sql})",
        f"CREATE POLICY usuarios_self_update ON public.usuarios FOR UPDATE TO PUBLIC "
        f"USING (id = {current_user_id_sql}) "
        f"WITH CHECK (id = {current_user_id_sql})",
        f"CREATE POLICY usuarios_self_delete ON public.usuarios FOR DELETE TO PUBLIC "
        f"USING (id = {current_user_id_sql})",
        "DROP POLICY IF EXISTS historicos_funcionais_backend_access ON public.historicos_funcionais",
        "DROP POLICY IF EXISTS historicos_funcionais_user_access ON public.historicos_funcionais",
        f"CREATE POLICY historicos_funcionais_backend_access ON public.historicos_funcionais FOR ALL TO PUBLIC "
        f"USING (current_setting('app.backend_access', true) = 'on') "
        f"WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        f"CREATE POLICY historicos_funcionais_user_access ON public.historicos_funcionais FOR ALL TO PUBLIC "
        f"USING (usuario_id = {current_user_id_sql}) "
        f"WITH CHECK (usuario_id = {current_user_id_sql})",
        "DROP POLICY IF EXISTS payroll_batches_backend_access ON public.payroll_batches",
        "DROP POLICY IF EXISTS payroll_batches_user_access ON public.payroll_batches",
        f"CREATE POLICY payroll_batches_backend_access ON public.payroll_batches FOR ALL TO PUBLIC "
        f"USING (current_setting('app.backend_access', true) = 'on') "
        f"WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        f"CREATE POLICY payroll_batches_user_access ON public.payroll_batches FOR ALL TO PUBLIC "
        f"USING (user_id = {current_user_id_sql}) "
        f"WITH CHECK (user_id = {current_user_id_sql})",
        "DROP POLICY IF EXISTS financeiro_importacoes_temporarias_backend_access ON public.financeiro_importacoes_temporarias",
        "DROP POLICY IF EXISTS financeiro_importacoes_temporarias_user_access ON public.financeiro_importacoes_temporarias",
        f"CREATE POLICY financeiro_importacoes_temporarias_backend_access ON public.financeiro_importacoes_temporarias FOR ALL TO PUBLIC "
        f"USING (current_setting('app.backend_access', true) = 'on') "
        f"WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        f"CREATE POLICY financeiro_importacoes_temporarias_user_access ON public.financeiro_importacoes_temporarias FOR ALL TO PUBLIC "
        f"USING (user_id = {current_user_id_sql}) "
        f"WITH CHECK (user_id = {current_user_id_sql})",
        "DROP POLICY IF EXISTS paychecks_backend_access ON public.paychecks",
        "DROP POLICY IF EXISTS paychecks_user_access ON public.paychecks",
        f"CREATE POLICY paychecks_backend_access ON public.paychecks FOR ALL TO PUBLIC "
        f"USING (current_setting('app.backend_access', true) = 'on') "
        f"WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        f"CREATE POLICY paychecks_user_access ON public.paychecks FOR ALL TO PUBLIC "
        f"USING (user_id = {current_user_id_sql}) "
        f"WITH CHECK (user_id = {current_user_id_sql})",
        "DROP POLICY IF EXISTS paycheck_items_backend_access ON public.paycheck_items",
        "DROP POLICY IF EXISTS paycheck_items_user_access ON public.paycheck_items",
        f"CREATE POLICY paycheck_items_backend_access ON public.paycheck_items FOR ALL TO PUBLIC "
        f"USING (current_setting('app.backend_access', true) = 'on') "
        f"WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        f"CREATE POLICY paycheck_items_user_access ON public.paycheck_items FOR ALL TO PUBLIC "
        f"USING (EXISTS ("
        f"SELECT 1 FROM public.paychecks "
        f"WHERE public.paychecks.id = public.paycheck_items.paycheck_id "
        f"AND public.paychecks.user_id = {current_user_id_sql}"
        f")) "
        f"WITH CHECK (EXISTS ("
        f"SELECT 1 FROM public.paychecks "
        f"WHERE public.paychecks.id = public.paycheck_items.paycheck_id "
        f"AND public.paychecks.user_id = {current_user_id_sql}"
        f"))",
        "DROP POLICY IF EXISTS support_document_access_grants_backend_access ON public.support_document_access_grants",
        "DROP POLICY IF EXISTS support_document_access_grants_user_access ON public.support_document_access_grants",
        f"CREATE POLICY support_document_access_grants_backend_access ON public.support_document_access_grants FOR ALL TO PUBLIC "
        f"USING (current_setting('app.backend_access', true) = 'on') "
        f"WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        f"CREATE POLICY support_document_access_grants_user_access ON public.support_document_access_grants FOR ALL TO PUBLIC "
        f"USING (user_id = {current_user_id_sql}) "
        f"WITH CHECK (user_id = {current_user_id_sql})",
        "DROP POLICY IF EXISTS work_schedules_backend_access ON public.work_schedules",
        "DROP POLICY IF EXISTS work_schedules_user_access ON public.work_schedules",
        f"CREATE POLICY work_schedules_backend_access ON public.work_schedules FOR ALL TO PUBLIC "
        f"USING (current_setting('app.backend_access', true) = 'on') "
        f"WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        f"CREATE POLICY work_schedules_user_access ON public.work_schedules FOR ALL TO PUBLIC "
        f"USING (user_id = {current_user_id_sql}) "
        f"WITH CHECK (user_id = {current_user_id_sql})",
        "DROP POLICY IF EXISTS vacation_periods_backend_access ON public.vacation_periods",
        "DROP POLICY IF EXISTS vacation_periods_user_access ON public.vacation_periods",
        f"CREATE POLICY vacation_periods_backend_access ON public.vacation_periods FOR ALL TO PUBLIC "
        f"USING (current_setting('app.backend_access', true) = 'on') "
        f"WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        f"CREATE POLICY vacation_periods_user_access ON public.vacation_periods FOR ALL TO PUBLIC "
        f"USING (user_id = {current_user_id_sql}) "
        f"WITH CHECK (user_id = {current_user_id_sql})",
        "DROP POLICY IF EXISTS work_calendar_overrides_backend_access ON public.work_calendar_overrides",
        "DROP POLICY IF EXISTS work_calendar_overrides_user_access ON public.work_calendar_overrides",
        f"CREATE POLICY work_calendar_overrides_backend_access ON public.work_calendar_overrides FOR ALL TO PUBLIC "
        f"USING (current_setting('app.backend_access', true) = 'on') "
        f"WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        f"CREATE POLICY work_calendar_overrides_user_access ON public.work_calendar_overrides FOR ALL TO PUBLIC "
        f"USING (user_id = {current_user_id_sql}) "
        f"WITH CHECK (user_id = {current_user_id_sql})",
    ]

    try:
        with engine.begin() as conexao:
            for comando in comandos:
                conexao.execute(text(comando))
    except Exception:
        logger.exception(
            "Falha ao habilitar RLS nas tabelas publicas",
            extra={"tabelas": ["usuarios", "historicos_funcionais", "financeiro"]},
        )

    if not SUPABASE_STORAGE_CONFIGURED:
        logger.info(
            "Supabase Storage nao configurado; politicas de bucket ignoradas",
            extra={"storage": "local"},
        )
        return

    bucket = SUPABASE_STORAGE_BUCKET.replace("'", "''")
    comandos_storage = [
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'storage' AND table_name = 'buckets'
            ) THEN
                UPDATE storage.buckets
                SET public = FALSE
                WHERE id = '{bucket}';
            END IF;
        END $$;
        """,
        "ALTER TABLE IF EXISTS storage.objects ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS storage.objects FORCE ROW LEVEL SECURITY",
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'storage' AND table_name = 'objects'
            ) THEN
                DROP POLICY IF EXISTS gestaocarreira_backend_objects_access ON storage.objects;
                CREATE POLICY gestaocarreira_backend_objects_access ON storage.objects FOR ALL TO PUBLIC
                USING (
                    bucket_id = '{bucket}'
                    AND current_setting('app.backend_access', true) = 'on'
                )
                WITH CHECK (
                    bucket_id = '{bucket}'
                    AND current_setting('app.backend_access', true) = 'on'
                );
            END IF;
        END $$;
        """,
    ]

    try:
        with engine.begin() as conexao:
            for comando in comandos_storage:
                conexao.execute(text(comando))
    except Exception:
        logger.exception(
            "Falha ao restringir bucket do Supabase Storage",
            extra={"bucket": SUPABASE_STORAGE_BUCKET},
        )


def sincronizar_usuario_table() -> None:
    comandos = [
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS apelido VARCHAR",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS login VARCHAR",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS senha_hash VARCHAR",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS token_confirmacao_email VARCHAR",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS email_confirmado BOOLEAN NOT NULL DEFAULT FALSE",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS data_exercicio DATE",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS sessao_token_hash VARCHAR",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS sessao_expira_em TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS redefinir_senha_token_hash VARCHAR",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS redefinir_senha_expira_em TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS politica_privacidade_aceita_em TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS politica_privacidade_versao VARCHAR",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS confirmado_em TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE IF EXISTS payroll_batches ADD COLUMN IF NOT EXISTS last_error_message VARCHAR NOT NULL DEFAULT ''",
        "ALTER TABLE IF EXISTS payroll_batches ADD COLUMN IF NOT EXISTS failure_messages TEXT NOT NULL DEFAULT '[]'",
        "ALTER TABLE IF EXISTS payroll_batches ADD COLUMN IF NOT EXISTS missing_competencies TEXT NOT NULL DEFAULT '[]'",
        "ALTER TABLE IF EXISTS payroll_batches ADD COLUMN IF NOT EXISTS duplicated_files INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE IF EXISTS payroll_batches ADD COLUMN IF NOT EXISTS processing_seconds_total NUMERIC(14,3) NOT NULL DEFAULT 0",
        "ALTER TABLE IF EXISTS paychecks ADD COLUMN IF NOT EXISTS file_hash VARCHAR NOT NULL DEFAULT ''",
        "ALTER TABLE IF EXISTS paychecks ADD COLUMN IF NOT EXISTS matricula VARCHAR NOT NULL DEFAULT ''",
        "ALTER TABLE IF EXISTS financeiro_importacoes_temporarias ADD COLUMN IF NOT EXISTS scope VARCHAR NOT NULL DEFAULT 'financeiro_importacao'",
        "ALTER TABLE IF EXISTS financeiro_importacoes_temporarias ADD COLUMN IF NOT EXISTS token_hash VARCHAR",
        "ALTER TABLE IF EXISTS financeiro_importacoes_temporarias ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE IF EXISTS financeiro_importacoes_temporarias ADD COLUMN IF NOT EXISTS used_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE IF EXISTS financeiro_importacoes_temporarias ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        "ALTER TABLE IF EXISTS support_document_access_grants ADD COLUMN IF NOT EXISTS document_kind VARCHAR NOT NULL DEFAULT 'unknown'",
        "ALTER TABLE IF EXISTS support_document_access_grants ADD COLUMN IF NOT EXISTS document_storage_path VARCHAR",
        "ALTER TABLE IF EXISTS support_document_access_grants ADD COLUMN IF NOT EXISTS reason TEXT",
        "ALTER TABLE IF EXISTS support_document_access_grants ADD COLUMN IF NOT EXISTS granted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        "ALTER TABLE IF EXISTS support_document_access_grants ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE IF EXISTS support_document_access_grants ADD COLUMN IF NOT EXISTS revoked_at TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE IF EXISTS support_document_access_grants ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        "ALTER TABLE IF EXISTS work_schedules ADD COLUMN IF NOT EXISTS name VARCHAR",
        "ALTER TABLE IF EXISTS work_schedules ADD COLUMN IF NOT EXISTS schedule_type VARCHAR",
        "ALTER TABLE IF EXISTS work_schedules ADD COLUMN IF NOT EXISTS anchor_date DATE",
        "ALTER TABLE IF EXISTS work_schedules ADD COLUMN IF NOT EXISTS state_code VARCHAR",
        "ALTER TABLE IF EXISTS work_schedules ADD COLUMN IF NOT EXISTS city_name VARCHAR",
        "ALTER TABLE IF EXISTS work_schedules ADD COLUMN IF NOT EXISTS working_weekdays_json TEXT NOT NULL DEFAULT '[]'",
        "ALTER TABLE IF EXISTS work_schedules ADD COLUMN IF NOT EXISTS custom_pattern_json TEXT NOT NULL DEFAULT '[]'",
        "ALTER TABLE IF EXISTS work_schedules ADD COLUMN IF NOT EXISTS note TEXT",
        "ALTER TABLE IF EXISTS work_schedules ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE",
        "ALTER TABLE IF EXISTS work_schedules ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        "ALTER TABLE IF EXISTS work_schedules ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        "ALTER TABLE IF EXISTS vacation_periods ADD COLUMN IF NOT EXISTS title VARCHAR NOT NULL DEFAULT 'Ferias'",
        "ALTER TABLE IF EXISTS vacation_periods ADD COLUMN IF NOT EXISTS vacation_type VARCHAR NOT NULL DEFAULT 'regular'",
        "ALTER TABLE IF EXISTS vacation_periods ADD COLUMN IF NOT EXISTS start_date DATE",
        "ALTER TABLE IF EXISTS vacation_periods ADD COLUMN IF NOT EXISTS end_date DATE",
        "ALTER TABLE IF EXISTS vacation_periods ADD COLUMN IF NOT EXISTS requested_days INTEGER",
        "ALTER TABLE IF EXISTS vacation_periods ADD COLUMN IF NOT EXISTS counted_days INTEGER",
        "ALTER TABLE IF EXISTS vacation_periods ADD COLUMN IF NOT EXISTS note TEXT",
        "ALTER TABLE IF EXISTS vacation_periods ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        "ALTER TABLE IF EXISTS vacation_periods ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        "ALTER TABLE IF EXISTS work_calendar_overrides ADD COLUMN IF NOT EXISTS override_date DATE",
        "ALTER TABLE IF EXISTS work_calendar_overrides ADD COLUMN IF NOT EXISTS is_working_day BOOLEAN",
        "ALTER TABLE IF EXISTS work_calendar_overrides ADD COLUMN IF NOT EXISTS title VARCHAR NOT NULL DEFAULT 'Excecao manual'",
        "ALTER TABLE IF EXISTS work_calendar_overrides ADD COLUMN IF NOT EXISTS note TEXT",
        "ALTER TABLE IF EXISTS work_calendar_overrides ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        "ALTER TABLE IF EXISTS work_calendar_overrides ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        "UPDATE financeiro_importacoes_temporarias SET scope = COALESCE(scope, 'financeiro_importacao') WHERE scope IS NULL",
        "ALTER TABLE IF EXISTS paycheck_items ADD COLUMN IF NOT EXISTS categoria_normalizada VARCHAR NOT NULL DEFAULT 'outros_vantagens'",
        "ALTER TABLE IF EXISTS paycheck_items ADD COLUMN IF NOT EXISTS descricao_original VARCHAR NOT NULL DEFAULT ''",
        "UPDATE usuarios SET apelido = COALESCE(apelido, '') WHERE apelido IS NULL",
        "UPDATE usuarios SET login = COALESCE(login, email) WHERE login IS NULL",
        "UPDATE usuarios SET senha_hash = COALESCE(senha_hash, '') WHERE senha_hash IS NULL",
        "UPDATE usuarios SET token_confirmacao_email = COALESCE(token_confirmacao_email, 'legacy-' || id::text) WHERE token_confirmacao_email IS NULL",
        "UPDATE usuarios SET email_confirmado = COALESCE(email_confirmado, FALSE) WHERE email_confirmado IS NULL",
        "UPDATE usuarios SET criado_em = COALESCE(criado_em, NOW()) WHERE criado_em IS NULL",
        "UPDATE payroll_batches SET last_error_message = COALESCE(last_error_message, '') WHERE last_error_message IS NULL",
        "UPDATE payroll_batches SET failure_messages = COALESCE(failure_messages, '[]') WHERE failure_messages IS NULL",
        "UPDATE payroll_batches SET missing_competencies = COALESCE(missing_competencies, '[]') WHERE missing_competencies IS NULL",
        "UPDATE payroll_batches SET duplicated_files = COALESCE(duplicated_files, 0) WHERE duplicated_files IS NULL",
        "UPDATE payroll_batches SET processing_seconds_total = COALESCE(processing_seconds_total, 0) WHERE processing_seconds_total IS NULL",
        "UPDATE paychecks SET file_hash = COALESCE(file_hash, '') WHERE file_hash IS NULL",
        "UPDATE paychecks SET matricula = COALESCE(matricula, '') WHERE matricula IS NULL",
        "ALTER TABLE IF EXISTS paychecks DROP CONSTRAINT IF EXISTS uq_paychecks_user_competencia",
    ]
    comandos.extend(
        [
            "ALTER TABLE IF EXISTS historicos_funcionais ADD COLUMN IF NOT EXISTS arquivo_storage_path VARCHAR",
            "ALTER TABLE IF EXISTS historicos_funcionais ADD COLUMN IF NOT EXISTS afastamentos_storage_path VARCHAR",
            "CREATE INDEX IF NOT EXISTS ix_usuarios_sessao_token_hash ON usuarios (sessao_token_hash)",
            "CREATE INDEX IF NOT EXISTS ix_usuarios_redefinir_senha_token_hash ON usuarios (redefinir_senha_token_hash)",
            "CREATE INDEX IF NOT EXISTS ix_historicos_funcionais_usuario_criado_em_id ON historicos_funcionais (usuario_id, criado_em DESC, id DESC)",
            "CREATE INDEX IF NOT EXISTS ix_financeiro_importacoes_temporarias_user_id_created_at ON financeiro_importacoes_temporarias (user_id, created_at DESC, id DESC)",
            "CREATE INDEX IF NOT EXISTS ix_financeiro_importacoes_temporarias_token_hash ON financeiro_importacoes_temporarias (token_hash)",
            "CREATE INDEX IF NOT EXISTS ix_financeiro_importacoes_temporarias_expires_at ON financeiro_importacoes_temporarias (expires_at)",
            "CREATE INDEX IF NOT EXISTS ix_paychecks_user_id_file_hash ON paychecks (user_id, file_hash)",
            "CREATE INDEX IF NOT EXISTS ix_paychecks_user_id_ano_mes_matricula ON paychecks (user_id, ano, mes, matricula)",
            "CREATE INDEX IF NOT EXISTS ix_support_document_access_grants_user_id_created_at ON support_document_access_grants (user_id, created_at DESC, id DESC)",
            "CREATE INDEX IF NOT EXISTS ix_support_document_access_grants_expires_at ON support_document_access_grants (expires_at)",
            "CREATE INDEX IF NOT EXISTS ix_work_schedules_user_id_is_active ON work_schedules (user_id, is_active)",
            "CREATE INDEX IF NOT EXISTS ix_work_schedules_user_id_created_at ON work_schedules (user_id, created_at DESC)",
            "CREATE INDEX IF NOT EXISTS ix_vacation_periods_user_id_start_date ON vacation_periods (user_id, start_date)",
            "CREATE INDEX IF NOT EXISTS ix_vacation_periods_user_id_end_date ON vacation_periods (user_id, end_date)",
            "CREATE INDEX IF NOT EXISTS ix_work_calendar_overrides_user_id_override_date ON work_calendar_overrides (user_id, override_date)",
        ]
    )

    with engine.begin() as conexao:
        Base.metadata.create_all(bind=conexao)
        for comando in comandos:
            conexao.execute(text(comando))


def criar_tabelas() -> None:
    sincronizar_usuario_table()
    habilitar_rls_tabelas_publicas()
    logger.info("Tabelas criadas com sucesso!", extra={"tabelas": "usuarios"})


if __name__ == "__main__":
    criar_tabelas()
