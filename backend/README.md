# Backend Python

Backend em Python com FastAPI, services e CLI.

## Como rodar

Servidor HTTP:

```powershell
..\run-backend.cmd
```

Se você ja estiver dentro da pasta `backend/`, pode usar:

```powershell
..\venv\Scripts\python.exe main.py
```

Terminal interativo:

```powershell
..\run-backend-cli.cmd
```

Se você ja estiver dentro da pasta `backend/`, pode usar:

```powershell
..\venv\Scripts\python.exe controllers\carreira_controller.py
```

Esses comandos usam o Python do `venv`. Voce nao precisa ativar o ambiente
manualmente toda vez.

## Estrutura

- `backend/models/` para entidades
- `backend/services/` para regras e calculos
- `backend/schemas/` para entrada e saida
- `backend/routes/` para rotas HTTP da API
- `backend/controllers/` para o fluxo de terminal
- `backend/app.py` para a aplicacao FastAPI
- `backend/main.py` para iniciar o servidor

## Endpoints

- `GET /api/health`
- `POST /api/carreira/resumo`
- `POST /api/usuarios`
- `GET /api/usuarios`
- `GET /api/usuarios/ultimo`
- `POST /api/usuarios/confirmar`
- `DELETE /api/usuarios/ultimo`

## Variaveis de ambiente

- As variaveis ficam em `backend/.env`
- `HOST`: host do servidor
- `PORT`: porta do servidor
- `CORS_ORIGINS`: origens liberadas para o front
- `DATABASE_URL`: string de conexao do banco PostgreSQL
- `FRONTEND_BASE_URL`: URL do frontend para montar o link de confirmacao
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`: dados do servidor de email
- `SMTP_USE_TLS`: liga ou desliga TLS no envio

O codigo nao repete esses valores em `main.py` nem em `app.py`. Ele le tudo do
arquivo `.env` centralizado em `backend/config.py`.

## Banco de dados e MVC

- `backend/database/` guarda a conexao com o PostgreSQL e o model ORM
- `backend/routes/` funciona como camada de controller da API
- `backend/services/` concentra as regras de negocio
- `backend/repositories/` faz o acesso direto ao banco

Na subida da API, o `app.py` chama `sincronizar_usuario_table()` para garantir
que as tabelas e colunas do usuario existam no banco.

## Fluxo de usuario

1. O formulario do front chama `POST /api/usuarios`.
2. O backend salva nome, apelido, email, login, senha hash e token de confirmacao.
3. Em seguida ele envia um email com o link de confirmacao para o endereco informado.
4. A pagina `/usuario` busca o cadastro mais recente em `GET /api/usuarios/ultimo`.
5. O link de email usa `/confirmar-email?token=...`.
6. A confirmacao chama `POST /api/usuarios/confirmar`.
7. O botao de limpeza remove o cadastro mais recente com `DELETE /api/usuarios/ultimo`.

## Regra de integracao

O front envia JSON para a API. A API converte isso em `Servidora`, chama o
service de calculo e devolve o resumo pronto para exibicao.
