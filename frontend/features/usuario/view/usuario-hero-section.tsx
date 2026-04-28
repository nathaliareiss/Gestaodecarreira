const destaques = [
  {
    titulo: "Cadastro simples",
    texto: "Preencha os dados e conclua sem etapas desnecessarias.",
  },
  {
    titulo: "Email automático",
    texto: "O sistema envia um email de confirmação para o endereço informado.",
  },
  {
    titulo: "Perfil organizado",
    texto: "Depois do envio, a pessoa vê o cadastro salvo e o status da conta.",
  },
]

export function UsuarioHeroSection() {
  return (
    <section className="hero">
      <div className="hero-copy">
        <p className="eyebrow">Cadastro de usuario</p>
        <h1>Cadastre a pessoa de forma simples e confirme por email.</h1>
        <p className="hero-text">
          O fluxo foi pensado para ser direto: preencha, envie e confirme pelo email
          recebido.
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
