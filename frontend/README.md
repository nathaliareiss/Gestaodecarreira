# Frontend

Aplicação Next.js responsável pela interface do sistema.

## O que aparece no frontend

- tela de cadastro
- tela de login
- recuperação de senha
- confirmação de e-mail
- página do usuário
- envio do histórico funcional em PDF
- envio opcional dos afastamentos
- gráficos e linha do tempo da carreira
- seletor de tema claro e escuro

## Como rodar

Na raiz do projeto:

```powershell
.\run-frontend.cmd
```

Dentro da pasta `frontend/`:

```powershell
npm run dev
```

## Variáveis de ambiente

- `NEXT_PUBLIC_API_URL`: URL pública do backend

As chamadas do frontend vão direto para o backend indicado em `NEXT_PUBLIC_API_URL`.
Não há URL padrão embutida no código: localmente use `frontend/.env.local` e, em produção,
defina a variável no ambiente de deploy.

O backend precisa responder CORS para a origem do frontend por meio de `CORS_ORIGINS`.

## Estrutura principal

- `frontend/app/`: rotas do App Router
- `frontend/features/`: módulos por domínio
- `frontend/shared/`: utilitários compartilhados

## Fluxo

1. `app/page.tsx` abre o cadastro.
2. `app/login/page.tsx` abre o login.
3. `app/usuario/page.tsx` abre o perfil do usuário.
4. O frontend consome a API por meio dos repositories.

## Observação

Os títulos e mensagens usam português como idioma principal, com alguns subtítulos em inglês para manter uma identidade visual consistente.
