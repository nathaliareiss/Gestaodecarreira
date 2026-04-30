# Backend FastAPI

API responsável por cadastro, login, confirmação de e-mail, recuperação de senha,
perfil do usuário e análise do histórico funcional.

## Como rodar

Servidor HTTP:

```powershell
..\run-backend.cmd
```

Terminal interativo:

```powershell
..\run-backend-cli.cmd
```

## Entrada de deploy

Para deploy, use o aplicativo FastAPI em:

```bash
backend.app:app
```

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Python 3.11+

## Estrutura

- `backend/routes/`: rotas HTTP
- `backend/services/`: regras de negócio
- `backend/repositories/`: acesso ao banco
- `backend/schemas/`: contratos de entrada e saída
- `backend/database/`: models e conexão com o banco

## Endpoints principais

### Auth

- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `POST /api/auth/solicitar-recuperacao-senha`
- `POST /api/auth/redefinir-senha`

### Usuários

- `POST /api/usuarios`
- `POST /api/usuarios/confirmar`
- `GET /api/usuarios/ultimo`
- `DELETE /api/usuarios/ultimo`

### Histórico funcional

- `POST /api/historicos-funcionais/analisar`
- `GET /api/historicos-funcionais/usuario/{usuario_id}/ultimo`
- `POST /api/historicos-funcionais/usuario/{usuario_id}/afastamentos`

### Outros

- `GET /api/health`

## Variáveis de ambiente

- `HOST`
- `PORT`
- `CORS_ORIGINS`
- `DATABASE_URL`
- `FRONTEND_BASE_URL`
- `EMAIL_CONFIRMATION_SUBJECT`
- `EMAIL_RECOVERY_SUBJECT`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `SMTP_FROM_NAME`
- `SMTP_USE_TLS`
- `SMTP_USE_SSL`

## E-mail

O sistema usa SMTP com a biblioteca nativa `smtplib` do Python.
Configure um servidor SMTP válido nas variáveis de ambiente para permitir o envio
de confirmação de cadastro e recuperação de senha.

## Fluxo

1. A API recebe o cadastro.
2. Salva os dados no banco.
3. Envia o e-mail de confirmação.
4. Libera o login depois da confirmação.
5. Recebe o PDF do histórico funcional.
6. Permite anexar afastamentos ao histórico salvo.
7. Retorna os cálculos e resumos para o frontend.

