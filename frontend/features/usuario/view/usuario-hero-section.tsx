const destaques = [
  {
    titulo: "Cadastro separado",
    texto: "A home agora so cadastra. Os dados vao para a pagina do usuario depois do envio.",
  },
  {
    titulo: "Confirmacao por email",
    texto: "O fluxo ja prepara um link de confirmacao para usar em uma API de envio de emails.",
  },
  {
    titulo: "Perfil salvo",
    texto: "Os dados ficam no navegador e podem ser exibidos e confirmados na rota /usuario.",
  },
]

export function UsuarioHeroSection() {
  return (
    <section className="hero">
      <div className="hero-copy">
        <p className="eyebrow">Cadastro de usuario</p>
        <h1>Cadastre a pessoa e leve os dados direto para a pagina do usuario.</h1>
        <p className="hero-text">
          O fluxo ficou mais limpo: a home recebe o cadastro, a rota /usuario mostra os
          dados salvos e a confirmacao de email fica pronta para receber uma API de envio.
        </p>
      </div>

      <div className="hero-grid">
        {destaques.map((destaque) => (
          <article className="mini-card" key={destaque.titulo}>
            <h2>{destaque.titulo}</h2>
            <p>{destaque.texto}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
