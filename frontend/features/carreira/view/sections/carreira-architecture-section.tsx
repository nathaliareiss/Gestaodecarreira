export function CarreiraArchitectureSection() {
  return (
    <section className="notes-grid">
      <article className="note-card">
        <p className="eyebrow">Como o front fala com o back</p>
        <h2>Fluxo de dados</h2>
        <ol>
          <li>Você preenche o formulário no Next.</li>
          <li>O front envia um POST /api/carreira/resumo em JSON.</li>
          <li>O backend monta a estrutura e roda os cálculos.</li>
          <li>A API devolve o resumo e o front organiza a resposta.</li>
        </ol>
      </article>

      <article className="note-card">
        <p className="eyebrow">Arquitetura</p>
        <h2>O que vive em cada camada</h2>
        <ul>
          <li>Model guarda os dados e o contrato.</li>
          <li>Repository faz a comunicação HTTP.</li>
          <li>Controller coordena o estado e as ações.</li>
          <li>View renderiza a interface sem regra de negócio.</li>
        </ul>
      </article>
    </section>
  )
}
