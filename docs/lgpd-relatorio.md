# Relatorio LGPD e Privacidade

Data da revisao: 10 de junho de 2026

## O que ja esta protegido

- Cadastro agora exige aceite explicito da Politica de Privacidade e o backend registra a confirmacao antes de criar a conta.
- Foi criada uma pagina publica de Politica de Privacidade em `frontend/app/politica-de-privacidade/page.tsx`.
- O backend passou a persistir versao e momento do aceite da politica de privacidade para novos cadastros.
- As tabelas com dados de usuario receberam RLS reforcado, com isolamento por `current_user_id` nas sessoes autenticadas e acesso privilegiado reservado para fluxos internos controlados.
- O bucket configurado do Supabase Storage agora e marcado como privado no bootstrap de schema e recebe policy para acesso interno autorizado.
- Logs estruturados passaram a mascarar e-mails, CPF, tokens, hashes, nomes de arquivos e caminhos sensiveis.
- Nao foram encontradas telas administrativas que exponham salarios, contracheques ou valores financeiros individualizados.
- Foi criada a estrutura de banco `support_document_access_grants` para um futuro fluxo de autorizacao temporaria e especifica por documento, sem acesso habilitado por padrao.

## O que ainda precisa ser corrigido

- Usuarios legados podem existir sem registro historico do aceite da politica. O ideal e exigir um novo aceite na proxima autenticacao desses perfis.
- A pagina de privacidade orienta a exclusao por canais oficiais, mas o produto ainda nao possui uma tela dedicada para o proprio usuario solicitar exclusao.
- O fluxo futuro de "Autorizar suporte" foi modelado no banco, mas ainda nao ha interface para conceder, limitar, revogar e auditar essa autorizacao.
- A aplicacao ainda possui fallback de armazenamento local e diretorios temporarios para PDFs. Em producao, isso precisa de politica de retencao, limpeza automatica e, de preferencia, criptografia em disco.
- As policies e a privacidade do bucket foram implementadas no codigo de sincronizacao. E necessario executar esse bootstrap ou migracao no ambiente real e validar o estado final no projeto Supabase de producao.

## Riscos de privacidade que permanecem

- Se o fallback local for usado por indisponibilidade do Supabase Storage, documentos sensiveis podem permanecer temporariamente no servidor da aplicacao.
- O repositorio contem arquivos de exemplo e diretorios temporarios de PDF; e importante revisar continuamente se nao ha artefatos reais sendo mantidos fora do ciclo previsto.
- O sistema ainda retorna CPF no painel da propria pessoa usuaria. Isso pode ser aceitavel funcionalmente, mas aumenta a responsabilidade sobre cache, screenshots e compartilhamento de tela.
- O observability stack local ainda usa credenciais padrao em desenvolvimento. Isso nao expoe dados em si, mas e uma configuracao fraca para qualquer ambiente compartilhado.

## Sugestoes adicionais para conformidade com a LGPD

- Implementar um fluxo de reconsentimento para contas antigas e registrar IP, user agent e timestamp do aceite.
- Criar uma central de privacidade com exclusao, exportacao de dados e historico de consentimentos.
- Definir prazo de retencao para PDFs temporarios, lotes financeiros, logs e cache, com limpeza automatica e auditoria.
- Adotar criptografia adicional para artefatos locais de contingencia e rotacao de secrets operacionais.
- Documentar base legal, operador/controlador, canal de atendimento e responsavel por privacidade na propria Politica de Privacidade.
- Adicionar testes automatizados de autorizacao cobrindo tentativas de acesso cruzado entre usuarios em todas as rotas com dados pessoais.
