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

## Variaveis de ambiente

- As variaveis ficam em `backend/.env`
- `HOST`: host do servidor
- `PORT`: porta do servidor
- `CORS_ORIGINS`: origens liberadas para o front

O codigo nao repete esses valores em `main.py` nem em `app.py`. Ele le tudo do
arquivo `.env` centralizado em `backend/config.py`.

## Regra de integracao

O front envia JSON para a API. A API converte isso em `Servidora`, chama o
service de calculo e devolve o resumo pronto para exibicao.
