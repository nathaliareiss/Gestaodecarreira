# Frontend

Aplicacao Next.js responsavel pela experiencia visual do sistema.

## O que o frontend faz

- mostra a tela de cadastro
- mostra a tela de login
- protege a pagina do usuario
- envia historico funcional em PDF
- exibe os calculos e os resumos vindos da API

## Como rodar

```powershell
..\run-frontend.cmd
```

Ou, dentro da pasta `frontend/`:

```powershell
npm run dev
```

## Dependencias de ambiente

- `NEXT_PUBLIC_API_URL`: URL do backend, por exemplo `http://localhost:8000`

## Estrutura Principal

- `frontend/app/`: rotas do App Router
- `frontend/features/`: features por dominio
- `frontend/shared/`: utilitarios compartilhados

## Fluxo

1. `app/page.tsx` abre o cadastro.
2. `app/login/page.tsx` abre o login.
3. `app/usuario/page.tsx` carrega a sessao autenticada.
4. O front conversa com a API por meio dos repositories.

## Observacao

O layout foi pensado para ser limpo e direto, sem excesso de blocos
explicativos para o usuario final.

