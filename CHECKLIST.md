# GestÃ£o de Carreira - Checklist

Ãšltima atualizaÃ§Ã£o: 2026-05-12

## Hoje

### ConcluÃ­do

- [x] Corrigida a rota `/usuario` para acesso direto sem depender da home.
- [x] Ajustado o fluxo da demo para abrir em `Career History`.
- [x] Padronizada a interface da demo em inglÃªs.
- [x] Corrigido o parser de contracheque para o PDF real de Minas Gerais.
- [x] Criada a primeira versÃ£o da aba `Finance` no frontend.
- [x] Ajustada a projeÃ§Ã£o salarial para crescimento composto anual.
- [x] Criada a arquitetura financeira em lote:
  - [x] `payroll_batches`
  - [x] `paychecks`
  - [x] `paycheck_items`
  - [x] endpoint de upload em lote
  - [x] worker dedicado
  - [x] endpoint de progresso
- [x] Corrigido o botÃ£o `Exit` para ficar fixo no fim da barra principal.
- [x] Corrigida a pÃ¡gina `/login` no frontend.
- [x] Criada a base de testes com `pytest` para o mÃ³dulo financeiro e para o parser.
- [x] Gerado o PDF de review do mÃ³dulo Financeiro.
- [x] Reduzido e padronizado o tamanho das imagens no `README`.
- [x] Reorganizado o `README` com versÃ£o em inglÃªs primeiro e portuguÃªs depois.
- [x] Corrigido o workflow antigo do GitHub Actions que dependia de `environment.yml`.
- [x] Implementada a experiÃªncia visual de upload em lote no frontend do Financeiro.
- [x] Adicionado polling automÃ¡tico do batch a cada 2 segundos.
- [x] Criados testes do frontend para o polling do lote.
- [x] Simplificada a tela do lote financeiro para ocultar a lista pesada de PDFs e mostrar barra de progresso.
- [x] Criado workflow de CI para o frontend com `lint`, `test` e `build`.
- [x] Adicionada a anÃ¡lise salarial anual com mediana por ano, grÃ¡fico de evoluÃ§Ã£o e resumo amigÃ¡vel no frontend.
- [x] Removida a pasta vazia `frontend/app/api`, que nÃ£o era usada pelo fluxo atual do frontend.
- [x] Padronizados em inglÃªs os tÃ­tulos e rÃ³tulos da seÃ§Ã£o de evoluÃ§Ã£o salarial do Financeiro.
- [x] Criada a base da importação automática de contracheques com token temporário, escopo limitado e upload dedicado para o helper Windows.
- [x] Adicionado o botão `Importar automaticamente` no frontend do Financeiro, com aviso específico para celular e reaproveitamento do upload manual.
- [x] Criada a tabela de sessão temporária de importação financeira com expiração, uso único e vínculo ao usuário autenticado.

### Em andamento

- [ ] Revisar o fluxo do lote financeiro no navegador com 5 PDFs.
- [ ] Validar o comportamento do worker em ambiente com Redis ativo.
- [ ] Conectar a nova experiÃªncia financeira ao frontend da demo, se necessÃ¡rio.

### PrÃ³ximos passos sugeridos

- [ ] Testar `POST /api/financeiro/upload-lote` com 5 PDFs reais.
- [ ] Testar `GET /api/financeiro/batch/{batch_id}` durante o processamento.
- [ ] Revisar a experiÃªncia demo do Financeiro para ficar mais clara para recrutadores.
- [ ] Confirmar se `/login` e `/usuario` continuam estÃ¡veis no deploy da Vercel.
- [ ] Validar o novo layout da barra de progresso no mobile.

## Como usar este checklist

- Marcar itens concluÃ­dos com `- [x]`.
- Adicionar novos passos em `Em andamento` ou `PrÃ³ximos passos sugeridos`.
- Se eu te passar uma nova tarefa, eu atualizo este arquivo para manter o ponto exato onde paramos.

## ObservaÃ§Ãµes

- Este checklist cobre sÃ³ o estado atual do projeto.
- A ideia Ã© manter o histÃ³rico curto, objetivo e fÃ¡cil de retomar depois.

- [x] Refatorada a anÃ¡lise financeira para separar salÃ¡rio-base, vantagens e descontos com composiÃ§Ã£o anual por categoria.
- [x] A rota de evoluÃ§Ã£o salarial passou a responder estado vazio sem 404 quando o lote nÃ£o tiver contracheques processados.
- [x] Padronizada a rota de evolucao salarial em GET /api/financeiro/evolucao-salarial e melhorado o erro para mostrar a URL chamada.
- [x] Mantida compatibilidade temporaria da evolucao salarial nos caminhos novo e legado para evitar 404 em deploys defasados.
- [x] Diagnosticada e registrada no startup a rota financeira de evolucao salarial, com compatibilidade da rota legada e rota final em GET /api/financeiro/evolucao-salarial.
- [x] Expostas mensagens de erro importantes do lote financeiro no status e na tela para substituir o erro genérico failed.
- [x] Diagnosticada a falha do upload-lote: o schema de payroll_batches em producao nao tinha last_error_message/failure_messages e o insert quebrava antes do worker.
- [x] Simplified the Financeiro screen to use lightweight annual line charts, a compact discounts table, and a collapsed Ver detalhes file list.

- [x] Financeiro now reloads saved contracheques from PostgreSQL on refresh using user-scoped endpoints.

- [x] Adicionado hash SHA-256 e chave de negocio para deduplicar contracheques por usuario, competencia e matricula, com batch contabilizando processados, duplicados e falhas.
- [x] Financeiro agora agenda 1 job por PDF, registra tempos por arquivo e fecha o lote com contadores atomicos para suportar filas paralelas.
- [x] Endurecida a autenticacao com token HttpOnly no backend, cookie de usuario minimalista no front e CORS com credenciais.
- [x] Financeiro passou a ignorar `user_id` do cliente e a buscar tudo a partir do usuario autenticado.
- [x] Historico funcional passou a usar o usuario autenticado para salvar e consultar, bloqueando acesso por `usuario_id` manual.
- [x] Sanitizados os logs de auth e cadastro para remover e-mail, login e outros identificadores sensiveis.
- [x] Removido o botao Use Example do cadastro, mantendo apenas o modo demo para a entrada de dados de exemplo.
- [x] Financeiro demo agora carrega uma evolucao salarial falsa baseada nos contracheques reais de 2015 e 2026, sem chamar o backend.
- [x] Corrigida a sessao de autenticacao para usar SameSite=None em ambiente cross-origin seguro, evitando 401 no /api/auth/me e o retorno indevido para o cadastro.
- [x] Corrigido o loop de login: a pagina de login agora valida o token real de sessao e a area protegida volta para /login quando a sessao nao for valida, evitando cair no cadastro.
