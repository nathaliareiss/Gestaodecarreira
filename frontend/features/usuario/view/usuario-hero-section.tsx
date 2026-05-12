import { useLanguage } from "@/shared/i18n/language-provider"

type UsuarioHeroSectionProps = {
  entrandoDemo: boolean
  onEntrarDemo: () => void
  onAbrirLogin?: () => void
}

export function UsuarioHeroSection({
  entrandoDemo,
  onEntrarDemo,
  onAbrirLogin,
}: UsuarioHeroSectionProps) {
  const { texts } = useLanguage()

  return (
    <div className="hero-copy hero-copy--register hero-copy--centered">
      <div className="hero-topbar hero-topbar--register">
        <p className="eyebrow">{texts.authHero.signUpLabel}</p>
        <div className="hero-login-cta">
          <p className="hero-login-note">{texts.authHero.alreadyHaveAccount}</p>
          <button
            className="primary-button ghost-button--compact hero-login-button"
            type="button"
            onClick={onEntrarDemo}
            disabled={entrandoDemo}
          >
            {entrandoDemo ? texts.authHero.enteringDemo : texts.authHero.enterDemo}
          </button>
          <button
            className="ghost-button ghost-button--compact hero-login-button"
            type="button"
            onClick={onAbrirLogin}
          >
            {texts.authHero.signIn}
          </button>
        </div>
      </div>

      <div className="hero-center-stack">
        <p className="hero-subtitle hero-subtitle--centered">{texts.authHero.subtitle}</p>
        <h1 className="hero-title hero-title--centered hero-title--register">
          <span>{texts.authHero.titleLine1}</span>
          <span>{texts.authHero.titleLine2}</span>
        </h1>
        <p className="hero-text hero-text--centered">{texts.authHero.description}</p>
      </div>
    </div>
  )
}
