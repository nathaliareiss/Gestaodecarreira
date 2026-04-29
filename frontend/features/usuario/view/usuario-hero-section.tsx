import Link from "next/link"

export function UsuarioHeroSection() {
  return (
    <div className="hero-copy hero-copy--register">
      <div className="hero-topbar">
        <p className="eyebrow">Cadastro de usuario</p>
        <Link className="ghost-button ghost-button--compact" href="/login">
          Ja tenho conta
        </Link>
      </div>

      <h1>Career Progression Analyzer</h1>
      <p className="hero-subtitle">
        Analise a progressao funcional em portugues, com cadastro rapido e perfil
        organizado para acompanhar a evolucao da pessoa.
      </p>
      <p className="hero-text">
        A lateral de cadastro foi pensada para ser objetiva: preencha os dados
        principais, inclua a data de exercicio e siga para o perfil sem ruido visual.
      </p>
    </div>
  )
}
