# GestÃ£o de Carreira - Checklist

Ãšltima atualizaÃ§Ã£o: 2026-05-14

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
- [x] Criada a base da importaÃ§Ã£o automÃ¡tica de contracheques com token temporÃ¡rio, escopo limitado e upload dedicado para o helper Windows.
- [x] Adicionado o botÃ£o `Importar automaticamente` no frontend do Financeiro, com aviso especÃ­fico para celular e reaproveitamento do upload manual.
- [x] Criada a tabela de sessÃ£o temporÃ¡ria de importaÃ§Ã£o financeira com expiraÃ§Ã£o, uso Ãºnico e vÃ­nculo ao usuÃ¡rio autenticado.
- [x] Gerado o executÃ¡vel distribuÃ­vel `GestaoDeCarreira-Assistente.exe` a partir de `helper-contracheques/main.py` com PyInstaller.
- [x] Preparado o helper com `playwright`, `requests`, `python-dotenv` e `pyinstaller`, alÃ©m de `build.bat`, `helper.spec` e README de build.
- [x] Publicado o download do assistente em `backend/static/downloads/gestao-de-carreira-assistente.exe` para servir em `/downloads/gestao-de-carreira-assistente.exe`.

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
- [x] Padronizada a rota de evoluÃ§Ã£o salarial em GET /api/financeiro/evolucao-salarial e melhorado o erro para mostrar a URL chamada.
- [x] Mantida compatibilidade temporÃ¡ria da evoluÃ§Ã£o salarial nos caminhos novo e legado para evitar 404 em deploys defasados.
- [x] Diagnosticada e registrada no startup a rota financeira de evoluÃ§Ã£o salarial, com compatibilidade da rota legada e rota final em GET /api/financeiro/evolucao-salarial.
- [x] Expostas mensagens de erro importantes do lote financeiro no status e na tela para substituir o erro genÃ©rico failed.
- [x] Diagnosticada a falha do upload-lote: o schema de payroll_batches em produÃ§Ã£o nÃ£o tinha last_error_message/failure_messages e o insert quebrava antes do worker.
- [x] Simplified the Financeiro screen to use lightweight annual line charts, a compact discounts table, and a collapsed Ver detalhes file list.

- [x] Financeiro now reloads saved contracheques from PostgreSQL on refresh using user-scoped endpoints.

- [x] Adicionado hash SHA-256 e chave de negÃ³cio para deduplicar contracheques por usuÃ¡rio, competÃªncia e matrÃ­cula, com batch contabilizando processados, duplicados e falhas.
- [x] Financeiro agora agenda 1 job por PDF, registra tempos por arquivo e fecha o lote com contadores atÃ´micos para suportar filas paralelas.
- [x] Endurecida a autenticaÃ§Ã£o com token HttpOnly no backend, cookie de usuÃ¡rio minimalista no front e CORS com credenciais.
- [x] Financeiro passou a ignorar `user_id` do cliente e a buscar tudo a partir do usuÃ¡rio autenticado.
- [x] HistÃ³rico funcional passou a usar o usuÃ¡rio autenticado para salvar e consultar, bloqueando acesso por `usuario_id` manual.
- [x] Sanitizados os logs de auth e cadastro para remover e-mail, login e outros identificadores sensÃ­veis.
- [x] Removido o botÃ£o Use Example do cadastro, mantendo apenas o modo demo para a entrada de dados de exemplo.
- [x] Financeiro demo agora carrega uma evoluÃ§Ã£o salarial falsa baseada nos contracheques reais de 2015 e 2026, sem chamar o backend.
- [x] Corrigida a sessÃ£o de autenticaÃ§Ã£o para usar SameSite=None em ambiente cross-origin seguro, evitando 401 no /api/auth/me e o retorno indevido para o cadastro.
- [x] Corrigido o loop de login: a pÃ¡gina de login agora valida o token real de sessÃ£o e a Ã¡rea protegida volta para /login quando a sessÃ£o nÃ£o for vÃ¡lida, evitando cair no cadastro.

## Hoje - 2026-05-14

### Concluido

- [x] Refatorada a tela inicial de autenticacao para voltar ao tamanho anterior dos cards e manter a responsividade no mobile.
- [x] Ajustada a experiencia de autenticacao para manter os dois cards alinhados e sem mexer na regra de negocio.
- [x] Separada a UX do Financeiro em download do instalador, iniciar importacao automatica e fallback manual de token.
- [x] Gerado e publicado o instalador real do helper Windows com Inno Setup em `GestaoDeCarreira-Setup-1.0.3.exe`.
- [x] Atualizado o helper Windows para usar `https://portaldoservidor.mg.gov.br/`, aceitar protocolo customizado e registrar logs de inicializacao.
- [x] Corrigido o backend para servir `/downloads/GestaoDeCarreira-Setup-1.0.3.exe` a partir de `backend/static/downloads`.
- [x] Corrigidos os testes do backend financeiro para criar PDFs temporarios durante a execucao e nao depender de `_tmp_financeiro`.
- [x] Ajustada a pagina de perfil para reaproveitar melhor os dados do historico funcional.
- [x] Corrigido o lint `react-hooks/set-state-in-effect` no controller de perfil.
- [x] Padronizada a hierarquia visual dos titulos de `Financeiro` e `Historico funcional`.

### Em andamento

- [ ] Confirmar o deploy publicado no Railway/GitHub para que o download versionado apareca no site.
- [ ] Validar no Windows real o fluxo `Instalar assistente` -> `Ja tenho instalado: iniciar`.
- [ ] Testar a URL publica do instalador depois do proximo deploy.

### Notas rapidas

- O arquivo `backend/static/downloads/GestaoDeCarreira-Setup-1.0.3.exe` esta versionado no Git.
- A rota de download local responde `200` para o instalador versionado.
- O problema restante parece ser publicacao/deploy antigo, nao o arquivo local.

