import type { FormEvent } from "react"

import type {
  UsuarioLogin,
  UsuarioSolicitacaoRecuperacaoSenha,
} from "../model/auth.model"
import { useLanguage } from "@/shared/i18n/language-provider"

type LoginCardViewProps = {
  modo: "login" | "recuperacao"
  dados: UsuarioLogin
  recuperacao: UsuarioSolicitacaoRecuperacaoSenha
  carregando: boolean
  reenviandoConfirmacao: boolean
  recuperando: boolean
  erro: string | null
  mensagemConfirmacao: string | null
  erroConfirmacao: string | null
  erroRecuperacao: string | null
  mensagemRecuperacao: string | null
  onSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onRecuperacaoSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onReenviarConfirmacao: () => void
  onAbrirRecuperacao: () => void
  onVoltarLogin: () => void
  onLoginChange: (valor: string) => void
  onSenhaChange: (valor: string) => void
  onRecuperacaoEmailChange: (valor: string) => void
}

export function LoginCardView({
  modo,
  dados,
  recuperacao,
  carregando,
  reenviandoConfirmacao,
  recuperando,
  erro,
  mensagemConfirmacao,
  erroConfirmacao,
  erroRecuperacao,
  mensagemRecuperacao,
  onSubmit,
  onRecuperacaoSubmit,
  onReenviarConfirmacao,
  onAbrirRecuperacao,
  onVoltarLogin,
  onLoginChange,
  onSenhaChange,
  onRecuperacaoEmailChange,
}: LoginCardViewProps) {
  const { texts } = useLanguage()

  return (
    <>
      {modo === "login" ? (
        <form className="card form-card form-card--login form-card--auth" onSubmit={onSubmit}>
          <div className="card-header card-header--tight card-header--stacked">
            <div>
              <p className="eyebrow">{texts.authCard.access}</p>
              <h2>{texts.authCard.signIn}</h2>
            </div>
          </div>

          <label className="field">
            <span>{texts.authCard.loginOrEmail}</span>
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
            <span>{texts.authCard.password}</span>
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
            <button className="primary-button button--large auth-card__primary" type="submit" disabled={carregando}>
              {carregando ? texts.authCard.signingIn : texts.authCard.signIn}
            </button>
          </div>

          <div className="auth-card-links auth-card-links--center" aria-label="Account links">
            <button
              className="ghost-button ghost-button--text"
              type="button"
              onClick={onAbrirRecuperacao}
            >
              {texts.authCard.forgotPassword}
            </button>
            <button
              className="ghost-button ghost-button--text"
              type="button"
              onClick={onReenviarConfirmacao}
              disabled={reenviandoConfirmacao}
            >
              {reenviandoConfirmacao
                ? texts.authCard.sendingLink
                : texts.authCard.resendConfirmation}
            </button>
          </div>

          {mensagemConfirmacao ? <p className="success-box">{mensagemConfirmacao}</p> : null}
          {erroConfirmacao ? <p className="error-box">{erroConfirmacao}</p> : null}
          {erro ? <p className="error-box">{erro}</p> : null}
        </form>
      ) : (
        <form className="card form-card form-card--recovery form-card--auth" onSubmit={onRecuperacaoSubmit}>
          <div className="card-header card-header--tight card-header--stacked">
            <div>
              <p className="eyebrow">{texts.authCard.accessHelp}</p>
              <h2>{texts.authCard.forgotPassword}</h2>
            </div>
            <button className="ghost-button ghost-button--compact" type="button" onClick={onVoltarLogin}>
              {texts.authCard.back}
            </button>
          </div>

          <p className="helper">{texts.authCard.enterEmailOnly}</p>

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
            <button className="primary-button button--large" type="submit" disabled={recuperando}>
              {recuperando ? texts.authCard.sendingLink : texts.authCard.sendLink}
            </button>
          </div>

          {mensagemRecuperacao ? <p className="success-box">{mensagemRecuperacao}</p> : null}
          {erroRecuperacao ? <p className="error-box">{erroRecuperacao}</p> : null}
        </form>
      )}
    </>
  )
}
