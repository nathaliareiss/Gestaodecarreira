import Link from "next/link"
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
  recuperando: boolean
  erro: string | null
  erroRecuperacao: string | null
  mensagemRecuperacao: string | null
  onSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onRecuperacaoSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onAbrirRecuperacao: () => void
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
  recuperando,
  erro,
  erroRecuperacao,
  mensagemRecuperacao,
  onSubmit,
  onRecuperacaoSubmit,
  onAbrirRecuperacao,
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
          <p className="eyebrow">Entrar</p>
          <h1>Acesse seu perfil e acompanhe seu historico.</h1>

          <div className="hero-links hero-links--top">
            <Link className="primary-button button--large" href="/">
              Criar conta
            </Link>
            <Link className="ghost-button button--large" href="/usuario">
              Ver perfil
            </Link>
          </div>

          <p className="hero-text">
            Entre com seu login ou email e a senha cadastrada para abrir sua pagina do
            usuario.
          </p>
        </div>

        <div className="login-panel">
          {modo === "login" ? (
            <form className="card form-card form-card--login" onSubmit={onSubmit}>
              <div className="card-header card-header--tight">
                <div>
                  <p className="eyebrow">Acesso</p>
                  <h2>Entrar no sistema</h2>
                </div>
              </div>

              <label className="field">
                <span>Login ou email</span>
                <input
                  value={dados.login}
                  onChange={(evento) => onLoginChange(evento.target.value)}
                  placeholder="maria.silva"
                  autoComplete="username"
                  required
                />
              </label>

              <label className="field">
                <span>Senha</span>
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
                  {carregando ? "Entrando..." : "Entrar"}
                </button>
                <button
                  className="ghost-button ghost-button--compact"
                  type="button"
                  onClick={onAbrirRecuperacao}
                >
                  Esqueci minha senha
                </button>
                <p className="helper">
                  Depois do login, voce vai para a pagina do usuario com acesso aos dados
                  e ao historico funcional.
                </p>
              </div>

              {erro ? <p className="error-box">{erro}</p> : null}
            </form>
          ) : (
            <form className="card form-card form-card--recovery" onSubmit={onRecuperacaoSubmit}>
              <div className="card-header card-header--tight">
                <div>
                  <p className="eyebrow">Ajuda de acesso</p>
                  <h2>Esqueci minha senha</h2>
                </div>
                <button
                  className="ghost-button ghost-button--compact"
                  type="button"
                  onClick={onVoltarLogin}
                >
                  Voltar
                </button>
              </div>

              <p className="helper">
                Informe apenas o seu email. Se ele estiver cadastrado, vamos enviar um
                link de redefinicao.
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
                  {recuperando ? "Enviando..." : "Enviar link de redefinicao"}
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
