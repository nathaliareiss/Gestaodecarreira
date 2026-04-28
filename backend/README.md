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
- `GOOGLE_GMAIL_CLIENT_FILE`: caminho do JSON OAuth do Google Cloud
- `GOOGLE_GMAIL_TOKEN_FILE`: arquivo gerado na primeira autorizacao do Gmail API
- `EMAIL_CONFIRMATION_SUBJECT`: assunto do email de confirmacao

O codigo nao repete esses valores em `main.py` nem em `app.py`. Ele le tudo do
arquivo `.env` centralizado em `backend/config.py`.

## Email de confirmacao

O envio usa a Gmail API com OAuth 2.0.

1. Crie ou escolha um projeto no Google Cloud Console.
2. Ative a Gmail API.
3. Configure a tela de consentimento OAuth.
4. Crie uma credencial OAuth Client ID.
5. Baixe o JSON da credencial e deixe em `backend/google_client_secret.json` ou em outro caminho ignorado pelo git.
6. Rode uma vez:

```powershell
..\venv\Scripts\python.exe -m backend.scripts.google_gmail_auth
```

Esse comando abre o navegador, voce entra com a conta que vai enviar os emails e o
arquivo `backend/google_token.json` e gerado automaticamente.

Se o Google reclamar do redirect, recrie a credencial como `Desktop app` ou adicione
um redirect localhost valido no OAuth client.

O arquivo `.env` fica fora do git, entao voce pode colocar ali o caminho local
do JSON sem vazar a credencial no commit.

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
3. Em seguida ele envia um email com o link de confirmacao pelo Gmail API.
4. A pagina `/usuario` busca o cadastro mais recente em `GET /api/usuarios/ultimo`.
5. O link de email usa `/confirmar-email?token=...`.
6. A confirmacao chama `POST /api/usuarios/confirmar`.
7. O botao de limpeza remove o cadastro mais recente com `DELETE /api/usuarios/ultimo`.

## Regra de integracao

O front envia JSON para a API. A API converte isso em `Servidora`, chama o
service de calculo e devolve o resumo pronto para exibicao.
