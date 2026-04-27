# Frontend

Aplicacao Next.js + React para visualizar e testar o backend Python de carreira.

## O que ela faz

- mostra um formulario para cadastro da servidora
- envia um `POST /api/carreira/resumo` para o backend
- exibe o resumo funcional em cards

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

```powershell
Copy-Item .env.example .env.local
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
