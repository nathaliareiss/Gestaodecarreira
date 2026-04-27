# Gestao de Carreira

Projeto com dois blocos separados:

- backend em Python
- frontend em Next.js + React

## Como rodar

Backend servidor:

```powershell
.\run-backend.cmd
```

Se voce estiver dentro de `backend/`, o equivalente direto em Python e:

```powershell
py main.py
```

Backend terminal:

```powershell
.\run-backend-cli.cmd
```

Se voce estiver dentro de `backend/`, o equivalente direto em Python e:

```powershell
py controllers\carreira_controller.py
```

Frontend:

```powershell
.\run-frontend.cmd
```

Ou, dentro de `frontend/`:

```powershell
npm run dev
```

## Estrutura

- `backend/`: codigo Python, API FastAPI, CLI e testes
- `frontend/`: aplicacao Next.js separada para deploy isolado
- `backend/routes/`: rotas HTTP da API
- `backend/.env`: configuracao real do backend
- `frontend/.env.local`: configuracao real do frontend
- `run-backend.cmd`: atalho para subir a API
- `run-backend-cli.cmd`: atalho para o terminal interativo
- `run-frontend.cmd`: atalho para subir o Next

## Como o front e o back se ligam

1. O usuario preenche o formulario no Next.
2. O front envia um `POST /api/carreira/resumo` em JSON.
3. A API Python transforma a entrada em `Servidora`.
4. O service calcula o resumo funcional.
5. A API devolve o resultado em JSON.
6. O front monta os cards para leitura visual.

## Observacao

Os comandos novos usam o Python do `venv` direto, entao voce nao precisa ativar
o ambiente manualmente toda vez.
