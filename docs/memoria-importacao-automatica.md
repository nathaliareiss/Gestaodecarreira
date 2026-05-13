# Memória - Importação Automática de Contracheques

## O que foi criado

- Um **token temporário de importação** para o fluxo automático de contracheques.
- Um **card no frontend** com botão `Importar automaticamente`.
- Um **aviso para celular** dizendo que esse fluxo é só para computador/Windows.
- Um **endpoint dedicado** para usar esse token e reaproveitar o upload em lote que já existia.

## Ideia principal

O objetivo foi separar duas coisas:

1. **Sessão normal do site**
   - serve para login, navegação e uso da aplicação.
2. **Sessão temporária de importação**
   - serve apenas para baixar e enviar contracheques.
   - expira rápido.
   - não vale como login normal.
   - fica ligada ao usuário autenticado.

## Como o backend funciona

- O backend cria uma tabela própria para a importação temporária.
- Nela, o token não é salvo em texto puro.
- O sistema guarda apenas o **hash SHA-256** do token.
- A sessão temporária tem:
  - `user_id`
  - `scope`
  - `token_hash`
  - `expires_at`
  - `used_at`
  - `created_at`

## Fluxo da criação do token

1. O usuário clica em `Importar automaticamente`.
2. O frontend chama `POST /api/financeiro/importacao-temporaria`.
3. O backend gera um token seguro com `token_urlsafe`.
4. O backend calcula o hash do token com `sha256`.
5. O backend salva esse hash no banco com expiração de 30 minutos.
6. O token bruto volta na resposta para ser usado pelo helper local.

## Fluxo do uso do token

1. O helper local abre o navegador no portal do governo.
2. O usuário faz login manualmente.
3. Depois que a página de contracheques carregar, o helper baixa os PDFs.
4. O helper envia os PDFs para `POST /api/financeiro/importacao-temporaria/upload-lote`.
5. O backend valida o token com o header `X-Import-Token`.
6. Se estiver válido, o backend reaproveita o mesmo pipeline do upload em lote.
7. Depois do uso, o token é marcado como usado.

## Como o upload manual foi preservado

- O upload manual antigo continua em `POST /api/financeiro/upload-lote`.
- O miolo de processamento foi reaproveitado.
- Assim, a lógica de lotes, worker, deduplicação e persistência continua igual.

## Como o frontend foi montado

- O card do financeiro agora mostra a área de importação automática no desktop.
- Quando o token é criado, ele aparece na própria tela.
- No celular, aparece só um aviso de que o recurso é para Windows/computador.
- O upload manual continua logo abaixo, sem mudar o fluxo já conhecido.

## Bibliotecas usadas

- **FastAPI**: cria as rotas do backend.
- **SQLAlchemy**: modela a tabela nova e conversa com o banco.
- **Pydantic**: valida os payloads das rotas.
- **React / Next.js**: renderiza o card e controla o estado do botão.
- **CSS responsivo**: esconde/mostra o bloco certo em desktop e mobile.
- **hashlib**: gera o hash do token.
- **secrets**: gera token aleatório seguro.

## Por que isso é seguro

- O token expira.
- O token é de uso único.
- O token é salvo só em hash.
- O token vale apenas para importação de contracheques.
- O token não substitui a sessão normal do site.
- O login do gov.br continua manual.

## Arquivos principais

- [`backend/services/financeiro_importacao_service.py`](../backend/services/financeiro_importacao_service.py)
- [`backend/routes/financeiro_routes.py`](../backend/routes/financeiro_routes.py)
- [`backend/repositories/financeiro_repository.py`](../backend/repositories/financeiro_repository.py)
- [`backend/database/models.py`](../backend/database/models.py)
- [`frontend/features/financeiro/view/financeiro-view.tsx`](../frontend/features/financeiro/view/financeiro-view.tsx)
- [`frontend/features/financeiro/model/financeiro.repository.ts`](../frontend/features/financeiro/model/financeiro.repository.ts)
- [`frontend/shared/i18n/messages.ts`](../frontend/shared/i18n/messages.ts)

## Próximo passo

- Criar o helper local em Python + Playwright.
- Ele vai consumir esse token temporário e automatizar apenas o download dos PDFs depois do login manual do usuário.
