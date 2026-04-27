# Frontend

Aplicacao Next.js + React para visualizar e testar o backend Python de carreira.

## O que ela faz

- mostra um formulario para cadastro da servidora
- envia um `POST /api/carreira/resumo` para o backend
- exibe o resumo funcional em cards

## Estrutura

- `frontend/app/`: rota e layout globais
- `frontend/features/carreira/`: contrato, API, formatacao e UI da feature
- `frontend/features/carreira/components/`: formulario, resultados e container da feature
- `frontend/app/globals.css`: tema visual e responsividade

## Como rodar

1. Entre na pasta:

```powershell
cd frontend
```

2. Instale as dependencias:

```powershell
npm install
```

3. Configure a URL do backend:

Crie `frontend/.env.local` com:

```powershell
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Rode o front:

```powershell
npm run dev
```

## Variavel de ambiente

- `NEXT_PUBLIC_API_URL`: URL da API Python, por exemplo `http://localhost:8000`

## O que o front usa do backend

- `POST /api/carreira/resumo`
- `GET /api/health`

## Observacao importante

O campo `tem_tempo_clt_averbado` ja vai no payload e na resposta, mas ainda nao altera as regras de calculo. Ele fica pronto para evoluirmos depois.
