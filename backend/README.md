# Backend Python

API FastAPI responsavel por cadastro, login, confirmacao de email e analise do
historico funcional.

## Como Rodar

Servidor HTTP:

```powershell
..\run-backend.cmd
```

Terminal interativo:

```powershell
..\run-backend-cli.cmd
```

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Python 3.11+

## Estrutura

- `backend/routes/`: controllers HTTP
- `backend/services/`: regras de negocio
- `backend/repositories/`: acesso ao banco
- `backend/schemas/`: contratos de entrada e saida
- `backend/database/`: models e conexao com o banco

## Endpoints Principais

- `GET /api/health`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `POST /api/usuarios`
- `POST /api/usuarios/confirmar`
- `GET /api/usuarios/ultimo`
- `DELETE /api/usuarios/ultimo`
- `POST /api/carreira/resumo`

## Variaveis de Ambiente

- `HOST`
- `PORT`
- `CORS_ORIGINS`
- `DATABASE_URL`
- `FRONTEND_BASE_URL`
- `EMAIL_CONFIRMATION_SUBJECT`
- `EMAIL_RECOVERY_SUBJECT`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `SMTP_FROM_NAME`
- `SMTP_USE_TLS`
- `SMTP_USE_SSL`

## Email de Confirmacao

O sistema usa SMTP com a biblioteca nativa `smtplib` do Python. Configure um
servidor SMTP valido nas variaveis de ambiente para que o backend consiga enviar
o email de confirmacao e o link de redefinicao de senha.

## Recuperacao de Senha

- `POST /api/auth/solicitar-recuperacao-senha`
- `POST /api/auth/redefinir-senha`

## Fluxo

1. A API recebe o cadastro.
2. Salva os dados no banco.
3. Envia email de confirmacao.
4. Permite login so depois da confirmacao.
5. Mantem sessao autenticada para o front consultar a pagina do usuario.
6. Permite solicitar recuperacao de senha por email.
