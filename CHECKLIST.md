# Gestão de Carreira - Checklist

Última atualização: 2026-05-08

## Hoje

### Concluído

- [x] Corrigida a rota `/usuario` para acesso direto sem depender da home.
- [x] Ajustado o fluxo da demo para abrir em `Career History`.
- [x] Padronizada a interface da demo em inglês.
- [x] Corrigido o parser de contracheque para o PDF real de Minas Gerais.
- [x] Criada a primeira versão da aba `Finance` no frontend.
- [x] Ajustada a projeção salarial para crescimento composto anual.
- [x] Criada a arquitetura financeira em lote:
  - [x] `payroll_batches`
  - [x] `paychecks`
  - [x] `paycheck_items`
  - [x] endpoint de upload em lote
  - [x] worker dedicado
  - [x] endpoint de progresso
- [x] Corrigido o botão `Exit` para ficar fixo no fim da barra principal.
- [x] Corrigida a página `/login` no frontend.
- [x] Criada a base de testes com `pytest` para o módulo financeiro e para o parser.
- [x] Gerado o PDF de review do módulo Financeiro.
- [x] Reduzido e padronizado o tamanho das imagens no `README`.
- [x] Reorganizado o `README` com versão em inglês primeiro e português depois.
- [x] Corrigido o workflow antigo do GitHub Actions que dependia de `environment.yml`.
- [x] Implementada a experiência visual de upload em lote no frontend do Financeiro.
- [x] Adicionado polling automático do batch a cada 2 segundos.
- [x] Criados testes do frontend para o polling do lote.
- [x] Simplificada a tela do lote financeiro para ocultar a lista pesada de PDFs e mostrar barra de progresso.
- [x] Criado workflow de CI para o frontend com `lint`, `test` e `build`.
- [x] Adicionada a análise salarial anual com mediana por ano, gráfico de evolução e resumo amigável no frontend.
- [x] Removida a pasta vazia `frontend/app/api`, que não era usada pelo fluxo atual do frontend.
- [x] Padronizados em inglês os títulos e rótulos da seção de evolução salarial do Financeiro.

### Em andamento

- [ ] Revisar o fluxo do lote financeiro no navegador com 5 PDFs.
- [ ] Validar o comportamento do worker em ambiente com Redis ativo.
- [ ] Conectar a nova experiência financeira ao frontend da demo, se necessário.

### Próximos passos sugeridos

- [ ] Testar `POST /api/financeiro/upload-lote` com 5 PDFs reais.
- [ ] Testar `GET /api/financeiro/batch/{batch_id}` durante o processamento.
- [ ] Revisar a experiência demo do Financeiro para ficar mais clara para recrutadores.
- [ ] Confirmar se `/login` e `/usuario` continuam estáveis no deploy da Vercel.
- [ ] Validar o novo layout da barra de progresso no mobile.

## Como usar este checklist

- Marcar itens concluídos com `- [x]`.
- Adicionar novos passos em `Em andamento` ou `Próximos passos sugeridos`.
- Se eu te passar uma nova tarefa, eu atualizo este arquivo para manter o ponto exato onde paramos.

## Observações

- Este checklist cobre só o estado atual do projeto.
- A ideia é manter o histórico curto, objetivo e fácil de retomar depois.

- [x] Refatorada a análise financeira para separar salário-base, vantagens e descontos com composição anual por categoria.
- [x] A rota de evolução salarial passou a responder estado vazio sem 404 quando o lote não tiver contracheques processados.
- [x] Padronizada a rota de evolucao salarial em GET /api/financeiro/evolucao-salarial e melhorado o erro para mostrar a URL chamada.
- [x] Mantida compatibilidade temporaria da evolucao salarial nos caminhos novo e legado para evitar 404 em deploys defasados.
- [x] Diagnosticada e registrada no startup a rota financeira de evolucao salarial, com compatibilidade da rota legada e rota final em GET /api/financeiro/evolucao-salarial.
- [x] Expostas mensagens de erro importantes do lote financeiro no status e na tela para substituir o erro gen�rico failed.
- [x] Diagnosticada a falha do upload-lote: o schema de payroll_batches em producao nao tinha last_error_message/failure_messages e o insert quebrava antes do worker.
- [x] Simplified the Financeiro screen to use lightweight annual line charts, a compact discounts table, and a collapsed Ver detalhes file list.

- [x] Financeiro now reloads saved contracheques from PostgreSQL on refresh using user-scoped endpoints.

- [x] Adicionado hash SHA-256 e chave de negocio para deduplicar contracheques por usuario, competencia e matricula, com batch contabilizando processados, duplicados e falhas.
- [x] Financeiro agora agenda 1 job por PDF, registra tempos por arquivo e fecha o lote com contadores atomicos para suportar filas paralelas.
- [x] Endurecida a autenticacao com token HttpOnly no backend, cookie de usuario minimalista no front e CORS com credenciais.
- [x] Financeiro passou a ignorar `user_id` do cliente e a buscar tudo a partir do usuario autenticado.
- [x] Historico funcional passou a usar o usuario autenticado para salvar e consultar, bloqueando acesso por `usuario_id` manual.
- [x] Sanitizados os logs de auth e cadastro para remover e-mail, login e outros identificadores sensiveis.
