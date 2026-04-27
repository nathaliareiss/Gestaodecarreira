# Backend Python

O backend continua em Python e reaproveita as camadas que ja existiam:

- `models/` para entidades
- `services/` para regras e calculos
- `schemas/` para entrada e saida
- `controllers/` para o fluxo de terminal

Agora ele tambem expoe uma API FastAPI para o front em Next.

## Como rodar o terminal

```powershell
python main.py
```

## Como rodar a API

```powershell
gestao-carreira-api
```

Ou, se preferir chamar o servidor direto:

```powershell
uvicorn api:app --reload --port 8000
```

## Endpoints

- `GET /api/health`
- `POST /api/carreira/resumo`

## Variaveis de ambiente

- `HOST`: host do servidor, padrao `0.0.0.0`
- `PORT`: porta do servidor, padrao `8000`
- `CORS_ORIGINS`: origens liberadas para o front, padrao `http://localhost:3000`
- `UVICORN_RELOAD`: ativa reload em dev quando `true`

## Regra de integracao

O front envia JSON para a API. A API converte isso em `Servidora`, chama o service de calculo e devolve o resumo pronto para exibicao.
