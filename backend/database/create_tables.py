from sqlalchemy import text

from backend.database.database import Base, engine
from backend.database import models as database_models  # noqa: F401
from backend.logger import logger


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
        "UPDATE usuarios SET apelido = COALESCE(apelido, '') WHERE apelido IS NULL",
        "UPDATE usuarios SET login = COALESCE(login, email) WHERE login IS NULL",
        "UPDATE usuarios SET senha_hash = COALESCE(senha_hash, '') WHERE senha_hash IS NULL",
        "UPDATE usuarios SET token_confirmacao_email = COALESCE(token_confirmacao_email, 'legacy-' || id::text) WHERE token_confirmacao_email IS NULL",
        "UPDATE usuarios SET email_confirmado = COALESCE(email_confirmado, FALSE) WHERE email_confirmado IS NULL",
        "UPDATE usuarios SET criado_em = COALESCE(criado_em, NOW()) WHERE criado_em IS NULL",
    ]
    comandos.extend(
        [
            "ALTER TABLE IF EXISTS historicos_funcionais ADD COLUMN IF NOT EXISTS arquivo_storage_path VARCHAR",
            "ALTER TABLE IF EXISTS historicos_funcionais ADD COLUMN IF NOT EXISTS afastamentos_storage_path VARCHAR",
        ]
    )

    with engine.begin() as conexao:
        Base.metadata.create_all(bind=conexao)
        for comando in comandos:
            conexao.execute(text(comando))


def criar_tabelas() -> None:
    sincronizar_usuario_table()
    logger.info("Tabelas criadas com sucesso!", extra={"tabelas": "usuarios"})


if __name__ == "__main__":
    criar_tabelas()
