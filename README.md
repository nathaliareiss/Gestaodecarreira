# Gestao de Carreira

Aplicacao completa para cadastro de usuarias, confirmacao por email, login com sessao
e leitura de historico funcional para acompanhar carreira no servico publico.

## Visao Geral

- `backend/`: API FastAPI em Python
- `frontend/`: app Next.js para cadastro, login e visualizacao
- `backend/database/`: models e configuracao do PostgreSQL
- `backend/routes/`: controller HTTP da API
- `backend/services/`: regras de negocio
- `backend/repositories/`: acesso ao banco

## Principais Funcionalidades

- cadastro de usuario com confirmacao por email
- login com sessao autenticada
- pagina protegida de usuario
- upload e leitura de historico funcional em PDF
- calculos de carreira com resumo visual no front

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Next.js
- React
- TypeScript

## Como Rodar

### Backend

```powershell
.\run-backend.cmd
```

### Frontend

```powershell
.\run-frontend.cmd
```

## Configuracao

- `backend/.env`: configuracao do backend
- `frontend/.env.local`: URL da API do frontend
- `backend/.env.example`: exemplo com SMTP para envio de email

O envio de emails usa SMTP configurado no `.env` do backend.

## Fluxo da Aplicacao

1. A pessoa cria a conta.
2. O backend salva no banco e envia email de confirmacao.
3. A pessoa confirma o email.
4. A pessoa faz login.
5. O front abre a pagina protegida de usuario.
6. O historico funcional em PDF pode ser enviado e analisado.

## Estrutura de Pastas

```text
backend/
frontend/
run-backend.cmd
run-backend-cli.cmd
run-frontend.cmd
```

## Observacao

O projeto foi organizado para facilitar evolucao futura, com separacao entre
rotas, servicos, repositorios e telas do front.
