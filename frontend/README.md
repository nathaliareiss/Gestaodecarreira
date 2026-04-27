# Frontend

Aplicacao Next.js + React para visualizar e testar o backend Python de carreira.

## O que ela faz

- mostra um formulario para cadastro da servidora
- envia um `POST /api/carreira/resumo` para o backend
- exibe o resumo funcional em cards

## Estrutura

- `frontend/app/`: rota e layout globais
- `frontend/features/carreira/model/`: dados, contrato e acesso HTTP
- `frontend/features/carreira/controller/`: estado, acoes e coordenacao da feature
- `frontend/features/carreira/view/`: telas, componentes visuais e formatacao
- `frontend/app/globals.css`: tema visual e responsividade

## MVC no front

- Model guarda os dados e conversa com a API
- Controller controla o estado do formulario e do resultado
- View renderiza a interface sem conhecer a regra de negocio

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

Copie o exemplo:

```powershell
Copy-Item frontend\.env.local.example frontend\.env.local
```

O arquivo `frontend/.env.local` ja existe no projeto. Use esse passo so se quiser
recriar o arquivo do zero ou voltar ao padrao.

Se preferir criar do zero, use `frontend/.env.local` com:

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
