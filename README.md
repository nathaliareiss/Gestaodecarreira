# Gestão de Carreira

Aplicação para cadastro, login, confirmação por e-mail e análise de histórico funcional.
O foco é dar uma visão clara da carreira, com tempo trabalhado, afastamentos, próximos marcos
e processamento em fila para as tarefas mais pesadas.

## O que o sistema faz

- cadastro de usuário com confirmação por e-mail
- login com sessão autenticada
- recuperação de senha por e-mail
- página de perfil do usuário
- envio e leitura de histórico funcional em PDF
- envio opcional dos afastamentos em PDF
- filas para processamento de PDFs e e-mails
- gráficos de tempo trabalhado, tempo restante e afastamentos
- linha do tempo dos eventos da carreira
- alternância entre tema claro e escuro

## Estrutura

- `backend/`: API FastAPI em Python
- `frontend/`: aplicação Next.js
- `backend/queue/`: filas, jobs e worker
- `run-backend.cmd`: inicia o backend
- `run-frontend.cmd`: inicia o frontend

## Como rodar localmente

### Backend

```powershell
.\run-backend.cmd
```

### Frontend

```powershell
.\run-frontend.cmd
```

## Configuração

- `backend/.env`: variáveis do backend
- `frontend/.env.local`: URL da API consumida pelo frontend
- `backend/.env.example`: exemplo com SMTP, Redis e demais variáveis

### Variáveis importantes

- `DATABASE_URL`
- `REDIS_URL`
- `CORS_ORIGINS`
- `FRONTEND_BASE_URL`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`
- `SMTP_FROM_NAME`
- `SMTP_USE_TLS`
- `SMTP_USE_SSL`
- `NEXT_PUBLIC_API_URL`

## Deploy

- backend: use `backend.app:app`
- backend worker: execute `python -m backend.worker.worker`
- frontend: configure `NEXT_PUBLIC_API_URL` com a URL pública da API
- o link dos e-mails precisa usar a URL pública do frontend em `FRONTEND_BASE_URL`
- a fila precisa de `REDIS_URL`

## Fluxo principal

1. A pessoa cria a conta.
2. O backend salva os dados e agenda o e-mail de confirmação.
3. A pessoa confirma o cadastro e faz login.
4. A página do usuário mostra o perfil e o histórico funcional.
5. O histórico funcional e os afastamentos são lidos em PDF e convertidos em resumos visuais.
6. Quando Redis está disponível, esses PDFs entram na fila e o front acompanha o status.

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis + RQ
- Next.js
- React
- TypeScript

## Observabilidade

O backend expõe métricas em `GET /api/metrics` no formato Prometheus.

Para subir a stack local de coleta e visualização:

```powershell
.\run-observability.cmd
```

Isso inicia:

- Prometheus em `http://localhost:9090`
- Grafana em `http://localhost:3001`

Mais detalhes em [observability/README.md](observability/README.md).
