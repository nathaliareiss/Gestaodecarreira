import { useLanguage } from "@/shared/i18n/language-provider"

type AuthHeroSectionProps = {
  entrandoDemo: boolean
  onEntrarDemo: () => void
}

export function AuthHeroSection({ entrandoDemo, onEntrarDemo }: AuthHeroSectionProps) {
  const { texts } = useLanguage()

  return (
    <div className="hero-copy hero-copy--auth">
      <div className="auth-hero-stack">
        <h1 className="hero-title hero-title--auth">
          <span>{texts.authHero.titleLine1}</span>
          <span>{texts.authHero.titleLine2}</span>
        </h1>
        <p className="hero-text hero-text--auth">{texts.authHero.description}</p>
      </div>

      <button className="primary-button button--large auth-hero-button" type="button" onClick={onEntrarDemo} disabled={entrandoDemo}>
        {entrandoDemo ? texts.authHero.enteringDemo : texts.authHero.enterDemo}
      </button>
    </div>
  )
}
