import Link from "next/link"

type UsuarioHeroSectionProps = {
  entrandoDemo: boolean
  onEntrarDemo: () => void
}

export function UsuarioHeroSection({ entrandoDemo, onEntrarDemo }: UsuarioHeroSectionProps) {
  return (
    <div className="hero-copy hero-copy--register hero-copy--centered">
      <div className="hero-topbar hero-topbar--register">
        <p className="eyebrow">Sign Up</p>
        <div className="hero-login-cta">
          <p className="hero-login-note">Already have an account? Sign in here.</p>
          <button
            className="primary-button ghost-button--compact hero-login-button"
            type="button"
            onClick={onEntrarDemo}
            disabled={entrandoDemo}
          >
            {entrandoDemo ? "Entering demo..." : "Enter Demo With Sample Data"}
          </button>
          <Link className="ghost-button ghost-button--compact hero-login-button" href="/login">
            Sign In
          </Link>
        </div>
      </div>

      <div className="hero-center-stack">
        <p className="hero-subtitle hero-subtitle--centered">Career Manager</p>
        <h1 className="hero-title hero-title--centered hero-title--register">
          <span>Career</span>
          <span>Manager</span>
        </h1>
        <p className="hero-text hero-text--centered">
          Sign up to take control of your career in a practical way. Rest assured: your
          data will stay secure.
        </p>
      </div>
    </div>
  )
}
