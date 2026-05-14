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
    <div className="hero-copy hero-copy--register hero-copy--centered hero-copy--auth">
      <div className="auth-hero-stack auth-hero-stack--register">
        <h1 className="hero-title hero-title--auth hero-title--register">
          <span>{texts.authHero.titleLine1}</span>
          <span>{texts.authHero.titleLine2}</span>
        </h1>
        <p className="hero-text hero-text--centered">{texts.authHero.description}</p>
      </div>

      <div className="hero-links hero-links--auth">
        <button
          className="primary-button button--large"
          type="button"
          onClick={onEntrarDemo}
          disabled={entrandoDemo}
        >
          {entrandoDemo ? texts.authHero.enteringDemo : texts.authHero.enterDemo}
        </button>
        {onAbrirLogin ? (
          <button className="ghost-button ghost-button--compact" type="button" onClick={onAbrirLogin}>
            {texts.authCard.signIn}
          </button>
        ) : null}
      </div>
    </div>
  )
}
