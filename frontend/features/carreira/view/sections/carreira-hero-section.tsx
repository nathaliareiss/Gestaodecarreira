const blocos = [
  {
    titulo: "Backend Python",
    texto: "FastAPI recebe o JSON, usa os services existentes e devolve o resumo funcional.",
  },
  {
    titulo: "Frontend React",
    texto: "O formulario vive no cliente e faz fetch para a API com NEXT_PUBLIC_API_URL.",
  },
  {
    titulo: "Deploy separado",
    texto: "Cada pasta pode ir para um deploy diferente sem misturar runtime nem build.",
  },
]

export function CarreiraHeroSection() {
  return (
    <section className="hero">
      <div className="hero-copy">
        <p className="eyebrow">Gestao de Carreira</p>
        <h1>Visualize e teste a carreira em um front Next com backend Python.</h1>
        <p className="hero-text">
          O projeto ficou separado em duas camadas: o backend continua em Python, e o
          frontend em Next conversa com ele por HTTP para voce testar tudo de forma
          visual.
        </p>
      </div>

      <div className="hero-grid">
        {blocos.map((bloco) => (
          <article className="mini-card" key={bloco.titulo}>
            <h2>{bloco.titulo}</h2>
            <p>{bloco.texto}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
