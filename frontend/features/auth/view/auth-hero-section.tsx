import { useLanguage } from "@/shared/i18n/language-provider"

type AuthHeroSectionProps = {
  entrandoDemo: boolean
  onEntrarDemo: () => void
  onAbrirCadastro: () => void
}

export function AuthHeroSection({ entrandoDemo, onEntrarDemo, onAbrirCadastro }: AuthHeroSectionProps) {
  const { texts } = useLanguage()

  return (
    <div className="hero-copy hero-copy--auth">
      <div className="auth-hero-topbar">
        <button
          className="ghost-button ghost-button--compact auth-hero-demo"
          type="button"
          onClick={onEntrarDemo}
          disabled={entrandoDemo}
        >
          {entrandoDemo ? texts.authHero.enteringDemo : texts.authHero.enterDemo}
        </button>
      </div>

      <div className="auth-hero-stack">
        <h1 className="hero-title hero-title--auth">
          <span>{texts.authHero.titleLine1}</span>
          <span>{texts.authHero.titleLine2}</span>
        </h1>
        <p className="hero-text hero-text--auth">{texts.authHero.description}</p>
      </div>

      <div className="auth-hero-bottom">
        <span className="auth-hero-bottom__label">{texts.authHero.noAccount}</span>
        <button className="ghost-button ghost-button--compact auth-hero-signup" type="button" onClick={onAbrirCadastro}>
          {texts.authCard.createAccount}
        </button>
      </div>
    </div>
  )
}
