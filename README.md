# Gestao de Carreira

Projeto com dois blocos separados:

- backend em Python
- frontend em Next.js + React

A ideia e simples: o backend guarda as regras de carreira, e o front serve para voce visualizar, testar e evoluir a interface sem misturar as camadas.

## Estrutura

- `controllers/`, `models/`, `schemas/`, `services/`: backend Python atual
- `api.py`: entrada HTTP do backend
- `frontend/`: aplicacao Next.js isolada para deploy separado
- `tests/`: testes da regra de negocio em Python
- `backend/README.md`: guia do backend
- `frontend/README.md`: guia do front

## Como o front e o back se ligam

1. O usuario preenche o formulario no Next.
2. O front envia um `POST /api/carreira/resumo` em JSON.
3. A API Python transforma a entrada em `Servidora`.
4. O service calcula o resumo funcional.
5. A API devolve o resultado em JSON.
6. O front monta os cards para leitura visual.

## Rodar o backend

Terminal:

```powershell
python main.py
```

API:

```powershell
uvicorn api:app --reload --port 8000
```

## Rodar o frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Depois acesse o front e veja o formulario em acao.

## O que ja esta pronto

- cadastro pelo terminal
- calculos de carreira em services
- API FastAPI para consumo pelo front
- UI em Next para testar a API
- documentacao separada para backend e frontend

## Proximo passo natural

Podemos evoluir em duas direcoes:

1. adicionar novas regras de aposentadoria ao backend
2. transformar o front em uma tela mais completa com historico, validacao e exportacao
