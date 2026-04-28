import Link from "next/link"
import type { FormEvent } from "react"

import type { UsuarioLogin } from "../model/auth.model"

type LoginViewProps = {
  dados: UsuarioLogin
  carregando: boolean
  erro: string | null
  onSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onLoginChange: (valor: string) => void
  onSenhaChange: (valor: string) => void
}

export function LoginView({
  dados,
  carregando,
  erro,
  onSubmit,
  onLoginChange,
  onSenhaChange,
}: LoginViewProps) {
  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--login">
        <div className="hero-copy">
          <p className="eyebrow">Entrar</p>
          <h1>Acesse seu perfil e acompanhe seu histórico.</h1>
          <p className="hero-text">
            Entre com seu login ou email e a senha cadastrada para abrir sua página do
            usuário.
          </p>

          <div className="hero-links">
            <Link className="ghost-button" href="/">
              Criar conta
            </Link>
            <Link className="ghost-button" href="/usuario">
              Ver perfil
            </Link>
          </div>
        </div>

        <article className="mini-card">
          <h2>Login rapido</h2>
          <p>Sem passos extras. Se a conta estiver confirmada, voce entra na hora.</p>
        </article>
      </section>

      <section className="workbench workbench--single">
        <form className="card form-card" onSubmit={onSubmit}>
          <div className="card-header">
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

          <div className="actions">
            <button className="primary-button" type="submit" disabled={carregando}>
              {carregando ? "Entrando..." : "Entrar"}
            </button>
            <p className="helper">
              Depois do login, voce vai para a pagina do usuario com acesso aos dados e
              ao historico funcional.
            </p>
          </div>

          {erro ? <p className="error-box">{erro}</p> : null}
        </form>
      </section>
    </main>
  )
}

