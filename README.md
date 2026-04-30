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
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET`
- `SUPABASE_STORAGE_HISTORICO_PREFIX`
- `SUPABASE_STORAGE_AFASTAMENTOS_PREFIX`
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

## Storage

Os PDFs agora sÃ£o enviados para o Supabase Storage:

- bucket: `gestaocarreira`
- pasta de histÃ³rico funcional: `historicofuncional`
- pasta de afastamentos: `afastamentos`

O banco guarda apenas o caminho do arquivo e os metadados da anÃ¡lise.

Se o Supabase Storage não estiver acessível, o backend salva o PDF em um diretório local de
fallback (`backend/storage_data`) e marca a resposta com `armazenamento_origem: "local"`.

Se a fila do Redis cair, a API tenta processar direto no backend e marca a resposta com
`processamento_origem: "direto"`.

## Banco

O banco foi ajustado para responder melhor nas consultas mais comuns:

- autenticação por login, e-mail e token
- busca do último histórico funcional do usuário
- carregamento do painel sem depender de varredura completa de tabela

Na prática, isso deixa login e abertura da tela principal mais rápidos conforme os dados crescem.

## Cache

O backend também usa Redis como cache de leitura para reduzir consultas repetidas:

- último usuário
- último histórico funcional do usuário

As chaves têm TTL curto e são invalidadas automaticamente quando o banco é alterado, para evitar
respostas desatualizadas.

## Docker

As imagens do projeto ficaram separadas por serviço:

- backend: [Dockerfile](Dockerfile)
- frontend: [frontend/Dockerfile](frontend/Dockerfile)

O `Dockerfile` empacota só a aplicação. Banco e Redis ficam como serviços externos.
Para desenvolvimento local, o `docker-compose.yml` junta tudo na mesma rede:

- backend
- worker
- frontend
- postgres
- redis

### Compose local

Subir a stack inteira:

```powershell
docker compose up --build
```

Se quiser subir em segundo plano:

```powershell
docker compose up --build -d
```

Parar tudo:

```powershell
docker compose down
```

### Backend

Build:

```powershell
docker build -t gestao-carreira-backend .
```

Run:

```powershell
docker run --rm -p 8000:8000 --env-file backend/.env gestao-carreira-backend
```

### Frontend

Build:

```powershell
docker build -t gestao-carreira-frontend --build-arg NEXT_PUBLIC_API_URL=https://seu-backend.com -f frontend/Dockerfile frontend
```

Run:

```powershell
docker run --rm -p 3000:3000 gestao-carreira-frontend
```

### O que foi feito no Dockerfile

- `FROM`: escolhe a imagem base
- `WORKDIR`: define a pasta interna do container
- `COPY`: leva só o necessário para dentro da imagem
- `RUN`: instala dependências e faz build
- `EXPOSE`: documenta a porta usada pela aplicação
- `CMD`: define o comando final de inicialização

### Observação

O `compose` é para o ambiente local e de testes. No deploy, o backend continua usando as URLs do
serviço de banco e Redis configuradas no ambiente da plataforma.
Se o Docker Desktop não estiver rodando, o build falha com erro de conexão no daemon, como aconteceu
aqui nesta sessão.

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
