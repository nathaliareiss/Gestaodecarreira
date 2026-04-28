# Frontend

Aplicacao Next.js + React para visualizar e testar o backend Python de carreira.

## Como rodar

```powershell
..\run-frontend.cmd
```

Se a URL da API precisar mudar, ajuste `frontend/.env.local`.

Se você ja estiver dentro de `frontend/`, o comando direto e:

```powershell
npm run dev
```

## O que ela faz

- mostra um formulario para cadastro da servidora
- envia um `POST /api/carreira/resumo` para o backend
- exibe o resumo funcional em cards
- mostra o fluxo de cadastro de usuario integrado ao banco via API
- envia email de confirmacao no cadastro e confirma a conta pelo backend

## Estrutura

- `frontend/app/`: rota e layout globais do Next
- `frontend/features/carreira/controller/`: estado, acoes e coordenacao da feature
- `frontend/features/carreira/model/`: dados, contrato e acesso HTTP
- `frontend/features/carreira/view/`: composicao visual da feature
- `frontend/features/carreira/view/sections/`: secoes da pagina principal
- `frontend/features/usuario/controller/`: controller da pagina de usuario
- `frontend/features/usuario/model/`: tipos e acesso HTTP do fluxo de usuario
- `frontend/features/usuario/view/`: telas do fluxo de cadastro e confirmacao
- `frontend/shared/config/`: configuracoes compartilhadas, como URL da API
- `frontend/app/globals.css`: tema visual e responsividade

## MVC no front

- Model guarda os dados e conversa com a API
- Controller controla o estado do formulario e do resultado
- View renderiza a interface sem conhecer a regra de negocio

## Fluxo interno

1. `app/page.tsx` chama o controller da feature.
2. O controller usa o hook `use-carreira-controller`.
3. O hook conversa com o repository.
4. O repository chama o backend Python.
5. A view recebe os dados e monta a tela.

No fluxo de usuario:

1. `app/usuario/page.tsx` busca o cadastro mais recente no backend.
2. `features/usuario/controller/usuario-page-controller.tsx` renderiza a pagina.
3. O formulario em `use-usuario-controller.ts` envia o cadastro para `POST /api/usuarios`.
4. O backend envia o email de confirmacao com o link para `confirmar-email`.
5. A confirmacao de email usa `POST /api/usuarios/confirmar`.

## Variavel de ambiente

- `NEXT_PUBLIC_API_URL`: URL da API Python, por exemplo `http://localhost:8000`

## O que o front usa do backend

- `POST /api/carreira/resumo`
- `GET /api/health`
- `POST /api/usuarios`
- `GET /api/usuarios`
- `GET /api/usuarios/ultimo`
- `POST /api/usuarios/confirmar`
- `DELETE /api/usuarios/ultimo`

## Observacao importante

O campo `tem_tempo_clt_averbado` ja vai no payload e na resposta, mas ainda nao
altera as regras de calculo. Ele fica pronto para evoluirmos depois.
