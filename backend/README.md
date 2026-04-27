# Backend Python

Backend em Python com FastAPI, services e CLI.

## Como rodar

Servidor HTTP:

```powershell
..\run-backend.cmd
```

Se você ja estiver dentro da pasta `backend/`, pode usar:

```powershell
py main.py
```

Terminal interativo:

```powershell
..\run-backend-cli.cmd
```

Se você ja estiver dentro da pasta `backend/`, pode usar:

```powershell
py controllers\carreira_controller.py
```

Esses comandos usam o Python do sistema ou do atalho `.cmd`. Voce nao precisa
ativar o ambiente manualmente toda vez.

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

- `HOST`: host do servidor, padrao `0.0.0.0`
- `PORT`: porta do servidor, padrao `8000`
- `CORS_ORIGINS`: origens liberadas para o front, padrao `http://localhost:3000`

## Regra de integracao

O front envia JSON para a API. A API converte isso em `Servidora`, chama o
service de calculo e devolve o resumo pronto para exibicao.
