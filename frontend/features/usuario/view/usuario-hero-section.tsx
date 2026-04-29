import Link from "next/link"

export function UsuarioHeroSection() {
  return (
    <div className="hero-copy hero-copy--register hero-copy--centered">
      <div className="hero-topbar hero-topbar--register">
        <p className="eyebrow">Cadastre-se</p>
        <div className="hero-login-cta">
          <p className="hero-login-note">Ja tem conta? Entre por aqui.</p>
          <Link className="ghost-button ghost-button--compact hero-login-button" href="/login">
            Logar
          </Link>
        </div>
      </div>

      <div className="hero-center-stack">
        <p className="hero-subtitle hero-subtitle--centered">Career Manager</p>
        <h1 className="hero-title hero-title--centered">Gerenciador de carreira</h1>
        <p className="hero-text hero-text--centered">
          Cadastre-se para assumir o controle da sua carreira de forma prática. Fique
          tranquilo: seus dados estarão seguros e ninguém terá acesso a eles.
        </p>
      </div>
    </div>
  )
}
