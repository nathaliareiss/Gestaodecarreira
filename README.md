# Gestao de Carreira

Projeto com dois blocos separados:

- backend em Python
- frontend em Next.js + React

A ideia e simples: o backend guarda as regras de carreira, e o front serve para voce visualizar, testar e evoluir a interface sem misturar as camadas.

## Estrutura

- `backend/`: codigo Python, API FastAPI, CLI e testes
- `frontend/`: aplicacao Next.js isolada para deploy separado, organizada em MVC
- `backend/README.md`: guia do backend
- `frontend/README.md`: guia do front
- `backend/routes/`: rotas HTTP da API
- `backend/.env.example`: variaveis do backend
- `frontend/.env.local.example`: variaveis do frontend
- o arquivo real do backend fica em `backend/.env`
- o arquivo real do front fica em `frontend/.env.local`

## Como o front e o back se ligam

1. O usuario preenche o formulario no Next.
2. O front envia um `POST /api/carreira/resumo` em JSON.
3. A API Python transforma a entrada em `Servidora`.
4. O service calcula o resumo funcional.
5. A API devolve o resultado em JSON.
6. O front monta os cards para leitura visual.

## Rodar o backend

Servidor HTTP:

```powershell
.\venv\Scripts\Activate.ps1
python -m backend.main
```

Terminal interativo:

```powershell
.\venv\Scripts\Activate.ps1
gestao-carreira
```

O `backend/app.py` define a aplicacao FastAPI e registra as rotas de
`backend/routes/`. O `backend/main.py` so inicia o servidor.

Os arquivos reais de ambiente ja existem no projeto:

- `backend/.env`
- `frontend/.env.local`

Se quiser, edite esses arquivos diretamente. Os examples ficam como referencia.

## Rodar o frontend

```powershell
cd frontend
npm install
npm run dev
```

Se quiser mudar a URL da API, crie `frontend/.env.local` com `NEXT_PUBLIC_API_URL=http://localhost:8000`.

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
