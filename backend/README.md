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
- `GOOGLE_GMAIL_CLIENT_FILE`
- `GOOGLE_GMAIL_TOKEN_FILE`
- `GOOGLE_GMAIL_REDIRECT_HOST`
- `GOOGLE_GMAIL_REDIRECT_PORT`
- `EMAIL_CONFIRMATION_SUBJECT`

## Email de Confirmacao

O sistema usa Gmail API com OAuth 2.0. O arquivo OAuth fica localmente em
`backend/google_client_secret.json` e o token e gerado na primeira autorizacao.

## Fluxo

1. A API recebe o cadastro.
2. Salva os dados no banco.
3. Envia email de confirmacao.
4. Permite login so depois da confirmacao.
5. Mantem sessao autenticada para o front consultar a pagina do usuario.

