import type { FormEvent } from "react"

import type {
  UsuarioLogin,
  UsuarioSolicitacaoRecuperacaoSenha,
} from "../model/auth.model"

type LoginViewProps = {
  modo: "login" | "recuperacao"
  dados: UsuarioLogin
  recuperacao: UsuarioSolicitacaoRecuperacaoSenha
  carregando: boolean
  entrandoDemo: boolean
  reenviandoConfirmacao: boolean
  recuperando: boolean
  erro: string | null
  mensagemConfirmacao: string | null
  erroConfirmacao: string | null
  erroRecuperacao: string | null
  mensagemRecuperacao: string | null
  onSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onEntrarDemo: () => void
  onRecuperacaoSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onReenviarConfirmacao: () => void
  onAbrirRecuperacao: () => void
  onAbrirCadastro?: () => void
  onVoltarLogin: () => void
  onLoginChange: (valor: string) => void
  onSenhaChange: (valor: string) => void
  onRecuperacaoEmailChange: (valor: string) => void
}

export function LoginView({
  modo,
  dados,
  recuperacao,
  carregando,
  entrandoDemo,
  reenviandoConfirmacao,
  recuperando,
  erro,
  mensagemConfirmacao,
  erroConfirmacao,
  erroRecuperacao,
  mensagemRecuperacao,
  onSubmit,
  onEntrarDemo,
  onRecuperacaoSubmit,
  onReenviarConfirmacao,
  onAbrirRecuperacao,
  onAbrirCadastro,
  onVoltarLogin,
  onLoginChange,
  onSenhaChange,
  onRecuperacaoEmailChange,
}: LoginViewProps) {
  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--login">
        <div className="hero-copy hero-copy--login">
          <p className="eyebrow">Sign In</p>
          <h1>Access your profile and track your career.</h1>

          <div className="hero-links hero-links--top">
            <button
              className="primary-button button--large"
              type="button"
              onClick={onEntrarDemo}
              disabled={entrandoDemo}
            >
              {entrandoDemo ? "Entering demo..." : "Enter Demo With Sample Data"}
            </button>
            <button className="ghost-button button--large" type="button" onClick={onAbrirCadastro}>
              Create Account
            </button>
          </div>

          <p className="hero-text">
            Sign in with your login or email and password, or use the sample data to open the dashboard without creating an account.
          </p>
        </div>

        <div className="login-panel">
          {modo === "login" ? (
            <form className="card form-card form-card--login" onSubmit={onSubmit}>
              <div className="card-header card-header--tight">
                <div>
                  <p className="eyebrow">Access</p>
                  <h2>Sign In</h2>
                </div>
              </div>

              <label className="field">
                <span>Login or Email</span>
                <input
                  className="login-input"
                  value={dados.login}
                  onChange={(evento) => onLoginChange(evento.target.value)}
                  placeholder="maria.silva"
                  autoComplete="username"
                  required
                />
              </label>

              <label className="field">
                <span>Password</span>
                <input
                  type="password"
                  value={dados.senha}
                  onChange={(evento) => onSenhaChange(evento.target.value)}
                  placeholder="********"
                  autoComplete="current-password"
                  required
                />
              </label>

              <div className="actions actions--login">
                <button
                  className="primary-button button--large"
                  type="submit"
                  disabled={carregando}
                >
                  {carregando ? "Signing in..." : "Sign In"}
                </button>
                <button
                  className="ghost-button ghost-button--compact"
                  type="button"
                  onClick={onAbrirRecuperacao}
                >
                  Forgot Password
                </button>
                <div className="login-secondary-link">
                  <span className="login-secondary-link__label">Didn&apos;t receive the email?</span>
                  <button
                    className="ghost-button ghost-button--text"
                    type="button"
                    onClick={onReenviarConfirmacao}
                    disabled={reenviandoConfirmacao}
                  >
                    {reenviandoConfirmacao
                      ? "Resending confirmation..."
                      : "Resend Confirmation Email"}
                  </button>
                </div>
                <p className="helper">After signing in, you&apos;ll go to your page.</p>
              </div>

              {mensagemConfirmacao ? <p className="success-box">{mensagemConfirmacao}</p> : null}
              {erroConfirmacao ? <p className="error-box">{erroConfirmacao}</p> : null}
              {erro ? <p className="error-box">{erro}</p> : null}
            </form>
          ) : (
            <form className="card form-card form-card--recovery" onSubmit={onRecuperacaoSubmit}>
              <div className="card-header card-header--tight">
                <div>
                  <p className="eyebrow">Access Help</p>
                  <h2>Forgot Password</h2>
                </div>
                <button
                  className="ghost-button ghost-button--compact"
                  type="button"
                  onClick={onVoltarLogin}
                >
                  Back
                </button>
              </div>

              <p className="helper">
                Enter only your email. If it is registered, you will receive a link to create a new password.
              </p>

              <label className="field">
                <span>Email</span>
                <input
                  type="email"
                  value={recuperacao.email}
                  onChange={(evento) => onRecuperacaoEmailChange(evento.target.value)}
                  placeholder="maria@exemplo.com"
                  autoComplete="email"
                  required
                />
              </label>

              <div className="actions actions--compact">
                <button
                  className="primary-button button--large"
                  type="submit"
                  disabled={recuperando}
                >
                  {recuperando ? "Sending..." : "Send Link"}
                </button>
              </div>

              {mensagemRecuperacao ? <p className="success-box">{mensagemRecuperacao}</p> : null}
              {erroRecuperacao ? <p className="error-box">{erroRecuperacao}</p> : null}
            </form>
          )}
        </div>
      </section>
    </main>
  )
}
