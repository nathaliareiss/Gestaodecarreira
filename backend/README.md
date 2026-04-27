# Backend Python

O backend continua em Python e reaproveita as camadas que ja existiam:

- `backend/models/` para entidades
- `backend/services/` para regras e calculos
- `backend/schemas/` para entrada e saida
- `backend/controllers/` para o fluxo de terminal

Agora ele tambem expoe uma API FastAPI para o front em Next.

## Como rodar o terminal

1. Ative o ambiente virtual:

```powershell
.\venv\Scripts\Activate.ps1
```

2. Rode o terminal interativo:

```powershell
python -m backend.main
```

## Como rodar a API

Com o `venv` ativado:

```powershell
gestao-carreira-api
```

Ou, se preferir chamar o servidor direto:

```powershell
python -m uvicorn backend.api:app --reload --port 8000
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
