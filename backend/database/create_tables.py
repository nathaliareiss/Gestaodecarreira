from sqlalchemy import text

from backend.database.database import Base, engine
from backend.database import models as database_models  # noqa: F401
from backend.logger import logger


def habilitar_rls_tabelas_publicas() -> None:
    comandos = [
        "ALTER TABLE IF EXISTS public.usuarios ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.historicos_funcionais ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.payroll_batches ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.paychecks ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE IF EXISTS public.paycheck_items ENABLE ROW LEVEL SECURITY",
        "DROP POLICY IF EXISTS usuarios_backend_access ON public.usuarios",
        "CREATE POLICY usuarios_backend_access ON public.usuarios FOR ALL TO PUBLIC "
        "USING (current_setting('app.backend_access', true) = 'on') "
        "WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        "DROP POLICY IF EXISTS historicos_funcionais_backend_access ON public.historicos_funcionais",
        "CREATE POLICY historicos_funcionais_backend_access ON public.historicos_funcionais FOR ALL TO PUBLIC "
        "USING (current_setting('app.backend_access', true) = 'on') "
        "WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        "DROP POLICY IF EXISTS payroll_batches_backend_access ON public.payroll_batches",
        "CREATE POLICY payroll_batches_backend_access ON public.payroll_batches FOR ALL TO PUBLIC "
        "USING (current_setting('app.backend_access', true) = 'on') "
        "WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        "DROP POLICY IF EXISTS paychecks_backend_access ON public.paychecks",
        "CREATE POLICY paychecks_backend_access ON public.paychecks FOR ALL TO PUBLIC "
        "USING (current_setting('app.backend_access', true) = 'on') "
        "WITH CHECK (current_setting('app.backend_access', true) = 'on')",
        "DROP POLICY IF EXISTS paycheck_items_backend_access ON public.paycheck_items",
        "CREATE POLICY paycheck_items_backend_access ON public.paycheck_items FOR ALL TO PUBLIC "
        "USING (current_setting('app.backend_access', true) = 'on') "
        "WITH CHECK (current_setting('app.backend_access', true) = 'on')",
    ]

    try:
        with engine.begin() as conexao:
            for comando in comandos:
                conexao.execute(text(comando))
    except Exception:
        logger.exception(
            "Falha ao habilitar RLS nas tabelas publicas",
            extra={"tabelas": ["usuarios", "historicos_funcionais"]},
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
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()",
        "ALTER TABLE IF EXISTS usuarios ADD COLUMN IF NOT EXISTS confirmado_em TIMESTAMP WITH TIME ZONE",
        "ALTER TABLE IF EXISTS payroll_batches ADD COLUMN IF NOT EXISTS last_error_message VARCHAR NOT NULL DEFAULT ''",
        "ALTER TABLE IF EXISTS payroll_batches ADD COLUMN IF NOT EXISTS failure_messages TEXT NOT NULL DEFAULT '[]'",
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
    ]
    comandos.extend(
        [
            "ALTER TABLE IF EXISTS historicos_funcionais ADD COLUMN IF NOT EXISTS arquivo_storage_path VARCHAR",
            "ALTER TABLE IF EXISTS historicos_funcionais ADD COLUMN IF NOT EXISTS afastamentos_storage_path VARCHAR",
            "CREATE INDEX IF NOT EXISTS ix_usuarios_sessao_token_hash ON usuarios (sessao_token_hash)",
            "CREATE INDEX IF NOT EXISTS ix_usuarios_redefinir_senha_token_hash ON usuarios (redefinir_senha_token_hash)",
            "CREATE INDEX IF NOT EXISTS ix_historicos_funcionais_usuario_criado_em_id ON historicos_funcionais (usuario_id, criado_em DESC, id DESC)",
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
