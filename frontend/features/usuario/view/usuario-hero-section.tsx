import Link from "next/link"

export function UsuarioHeroSection() {
  return (
    <div className="hero-copy hero-copy--register hero-copy--centered">
      <div className="hero-topbar hero-topbar--register">
        <p className="eyebrow">Cadastre-se</p>
        <Link className="ghost-button ghost-button--compact" href="/login">
          Ja tenho conta
        </Link>
      </div>

      <p className="hero-subtitle hero-subtitle--centered">
         Career Manager
      </p>
      <h1>Gerenciador de carreira</h1>

      <p className="hero-text">
        Cadastre-se para assumir o controle da sua carreira de forma pratica. Fique
        tranquilo: seus dados estarao seguros e ninguem tera acesso a eles.
      </p>
    </div>
  )
}
