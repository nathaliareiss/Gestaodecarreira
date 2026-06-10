import Link from "next/link"

const DATA_VERSAO = "10 de junho de 2026"

export default function PoliticaDePrivacidadePage() {
  return (
    <main className="page-shell privacy-page">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="privacy-page__hero hero-copy">
        <p className="eyebrow">Privacidade</p>
        <h1>Politica de Privacidade</h1>
        <p className="hero-text hero-text--privacy">
          Esta plataforma trata dados pessoais apenas para entregar as analises de carreira e de
          contracheques da propria pessoa usuaria. Versao desta politica: {DATA_VERSAO}.
        </p>
        <div className="hero-links hero-links--privacy">
          <Link className="ghost-button" href="/">
            Voltar ao acesso
          </Link>
        </div>
      </section>

      <section className="notes-grid privacy-page__grid">
        <article className="note-card">
          <h2>Quais dados coletamos</h2>
          <ul>
            <li>Dados cadastrais do acesso, como nome, apelido, e-mail, login e data de exercicio.</li>
            <li>Dados de autenticacao e seguranca, como confirmacao de e-mail, hashes de senha e sessoes.</li>
            <li>Arquivos enviados pela propria pessoa usuaria, como historico funcional, afastamentos e contracheques.</li>
            <li>Dados extraidos desses documentos, como eventos funcionais, informacoes de carreira e valores financeiros necessarios para as analises.</li>
          </ul>
        </article>

        <article className="note-card">
          <h2>Como usamos esses dados</h2>
          <ul>
            <li>Os dados sao utilizados exclusivamente para gerar analises da carreira e dos contracheques do proprio usuario.</li>
            <li>Nao criamos telas administrativas para exposicao individual de salarios, contracheques ou documentos enviados.</li>
            <li>Funcionalidades internas devem trabalhar apenas com metricas agregadas e anonimizadas, como quantidade de usuarios e quantidade de arquivos processados.</li>
          </ul>
        </article>

        <article className="note-card">
          <h2>Armazenamento e acesso</h2>
          <ul>
            <li>Os documentos ficam em armazenamento privado, com restricao de acesso por contexto de usuario e por processos internos autorizados.</li>
            <li>As tabelas com dados pessoais usam politicas de isolamento para impedir acesso entre contas diferentes.</li>
            <li>Logs e monitoramento devem evitar CPF, salarios, contracheques, tokens e caminhos sensiveis de arquivos.</li>
          </ul>
        </article>

        <article className="note-card">
          <h2>Exclusao e suporte</h2>
          <ul>
            <li>Para solicitar exclusao de dados, entre em contato pelos canais oficiais de atendimento informando o e-mail da conta.</li>
            <li>A solicitacao deve incluir, se desejar, a remocao de historico funcional, contracheques e arquivos associados.</li>
            <li>Por padrao, a equipe nao acessa documentos enviados. No futuro, qualquer apoio tecnico a um documento especifico dependera de autorizacao temporaria da propria pessoa usuaria.</li>
          </ul>
        </article>
      </section>
    </main>
  )
}
