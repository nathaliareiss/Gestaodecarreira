# Backend Python

O backend continua em Python e reaproveita as camadas que ja existiam:

- `backend/models/` para entidades
- `backend/services/` para regras e calculos
- `backend/schemas/` para entrada e saida
- `backend/routes/` para rotas HTTP da API
  - `health_routes.py`
  - `carreira_routes.py`
- `backend/controllers/` para o fluxo de terminal
- `backend/app.py` para a aplicacao FastAPI
- `backend/main.py` para iniciar o servidor

Agora ele tambem expoe uma API FastAPI para o front em Next.

## Como rodar o terminal

1. Ative o ambiente virtual:

```powershell
.\venv\Scripts\Activate.ps1
```

2. Se quiser usar um arquivo de ambiente, copie o exemplo:

```powershell
Copy-Item backend\.env.example backend\.env
```

O arquivo `backend/.env` ja existe no projeto; use isso so se quiser recriar o
arquivo do zero ou voltar ao padrao.

3. Rode o terminal interativo:

```powershell
gestao-carreira
```

Esse comando e interativo e so fica disponivel depois de ativar o `venv`.
Se o PowerShell disser que o termo nao e reconhecido, rode o executavel direto:

```powershell
.\venv\Scripts\gestao-carreira.exe
```

Se voce abrir pelo botao de execucao da IDE sem um terminal com entrada, ele encerra
com a mensagem de que precisa de um terminal interativo.

## Como rodar a API

Com o `venv` ativado:

```powershell
python -m backend.main
```

Ou, se preferir chamar o servidor direto:

```powershell
python -m uvicorn backend.app:app --reload --port 8000
```

O backend le `backend/.env` automaticamente.

## Endpoints

- `GET /api/health`
- `POST /api/carreira/resumo`

As rotas ficam em `backend/routes/`, sao agrupadas por responsabilidade e sao registradas em `backend/app.py`.

## Variaveis de ambiente

- `HOST`: host do servidor, padrao `0.0.0.0`
- `PORT`: porta do servidor, padrao `8000`
- `CORS_ORIGINS`: origens liberadas para o front, padrao `http://localhost:3000`
- `UVICORN_RELOAD`: ativa reload em dev quando `true`

## Regra de integracao

O front envia JSON para a API. A API converte isso em `Servidora`, chama o service de calculo e devolve o resumo pronto para exibicao.
