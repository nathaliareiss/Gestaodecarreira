import Link from "next/link"

type UsuarioHeroSectionProps = {
  entrandoDemo: boolean
  onEntrarDemo: () => void
}

export function UsuarioHeroSection({ entrandoDemo, onEntrarDemo }: UsuarioHeroSectionProps) {
  return (
    <div className="hero-copy hero-copy--register hero-copy--centered">
      <div className="hero-topbar hero-topbar--register">
        <p className="eyebrow">Cadastre-se</p>
        <div className="hero-login-cta">
          <p className="hero-login-note">Ja tem conta? Entre por aqui.</p>
          <button
            className="primary-button ghost-button--compact hero-login-button"
            type="button"
            onClick={onEntrarDemo}
            disabled={entrandoDemo}
          >
            {entrandoDemo ? "Entrando no demo..." : "Entrar com dados de exemplo"}
          </button>
          <Link className="ghost-button ghost-button--compact hero-login-button" href="/login">
            Logar
          </Link>
        </div>
      </div>

      <div className="hero-center-stack">
        <p className="hero-subtitle hero-subtitle--centered">Career Manager</p>
        <h1 className="hero-title hero-title--centered hero-title--register">
          <span>Gerenciador de</span>
          <span>carreira</span>
        </h1>
        <p className="hero-text hero-text--centered">
          Cadastre-se para assumir o controle da sua carreira de forma prática. Fique
          tranquilo: seus dados estarão seguros.
        </p>
      </div>
    </div>
  )
}
