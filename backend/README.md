# Backend FastAPI

API responsável por cadastro, login, confirmação de e-mail, recuperação de senha,
perfil do usuário, histórico funcional e afastamentos.

## Como rodar

Servidor HTTP:

```powershell
..\run-backend.cmd
```

Terminal interativo:

```powershell
..\run-backend-cli.cmd
```

Worker das filas:

```powershell
.\venv\Scripts\python.exe -m backend.worker.worker
```

## Entrada de deploy

Para deploy, use a aplicação FastAPI em:

```bash
backend.app:app
```

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis + RQ para filas
- Python 3.11+

## Estrutura

- `backend/routes/`: rotas HTTP
- `backend/services/`: regras de negócio
- `backend/repositories/`: acesso ao banco
- `backend/schemas/`: contratos de entrada e saída
- `backend/database/`: models e conexão com o banco
- `backend/queue/`: filas, jobs e worker

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
- `GET /api/historicos-funcionais/jobs/{job_id}`
- `GET /api/historicos-funcionais/usuario/{usuario_id}/ultimo`
- `POST /api/historicos-funcionais/usuario/{usuario_id}/afastamentos`

### Outros

- `GET /api/health`
- `GET /api/metrics`  (formato Prometheus, para coleta por observabilidade)

## Variáveis de ambiente

- `HOST`
- `PORT`
- `REDIS_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET`
- `SUPABASE_STORAGE_HISTORICO_PREFIX`
- `SUPABASE_STORAGE_AFASTAMENTOS_PREFIX`
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

## Fila de processamento

As tarefas mais pesadas usam Redis + RQ:

- leitura do PDF do histórico funcional
- leitura dos afastamentos
- envio de e-mails de confirmação e recuperação

Quando `REDIS_URL` estiver configurado, a API agenda a tarefa e o frontend consulta o status em
`GET /api/historicos-funcionais/jobs/{job_id}`. Se a fila não estiver disponível, o backend faz
o processamento de forma direta para manter o ambiente local funcionando.

Se o Redis cair durante o envio, a API tenta seguir no modo direto em vez de parar na etapa de
agendamento. A resposta passa a indicar `processamento_origem: "direto"` quando isso acontece.

## Storage de PDFs

Os PDFs ficam no Supabase Storage:

- bucket: `gestaocarreira`
- pasta de histórico funcional: `historicofuncional`
- pasta de afastamentos: `afastamentos`

O backend recebe os arquivos via `multipart/form-data`, envia para o Storage e salva no banco
somente o caminho do objeto.

Se o Supabase Storage não estiver acessível, o backend salva o PDF em um diretório local de
fallback (`backend/storage_data`) e marca a resposta com `armazenamento_origem: "local"`.

## Otimizações de banco

As consultas mais frequentes receberam cuidado extra:

- busca de usuário por `login` e `email`
- recuperação de sessão por `sessao_token_hash`
- recuperação de redefinição de senha por `redefinir_senha_token_hash`
- busca do último histórico por usuário com índice composto em `usuario_id`, `criado_em` e `id`

Isso reduz varredura de tabela e acelera autenticação e carregamento do painel do histórico.

## Fluxo

1. A API recebe o cadastro.
2. Salva os dados no banco.
3. Agenda ou envia o e-mail de confirmação.
4. Libera o login depois da confirmação.
5. Recebe o PDF do histórico funcional.
6. Agenda o processamento na fila quando Redis estiver disponível.
7. Permite anexar afastamentos ao histórico salvo.
8. Retorna os cálculos e resumos para o frontend.
