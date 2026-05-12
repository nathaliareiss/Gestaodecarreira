import type { FormEvent } from "react"

import type { UsuarioCadastro } from "../model/usuario.model"

type UsuarioFormViewProps = {
  cadastro: UsuarioCadastro
  carregando: boolean
  erro: string | null
  mensagem: string | null
  onSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onNomeChange: (valor: string) => void
  onApelidoChange: (valor: string) => void
  onEmailChange: (valor: string) => void
  onDataExercicioChange: (valor: string) => void
  onLoginChange: (valor: string) => void
  onSenhaChange: (valor: string) => void
}

export function UsuarioFormView({
  cadastro,
  carregando,
  erro,
  mensagem,
  onSubmit,
  onNomeChange,
  onApelidoChange,
  onEmailChange,
  onDataExercicioChange,
  onLoginChange,
  onSenhaChange,
}: UsuarioFormViewProps) {
  return (
    <form className="card form-card form-card--register" onSubmit={onSubmit}>
      <div className="card-header card-header--tight">
        <div>
          <p className="eyebrow">New User</p>
          <h2>Access Details</h2>
        </div>
      </div>

      <label className="field">
        <span>Full Name</span>
        <input
          value={cadastro.nome}
          onChange={(evento) => onNomeChange(evento.target.value)}
          placeholder="Maria Silva"
          required
        />
      </label>

      <label className="field">
        <span>Nickname (optional)</span>
        <input
          value={cadastro.apelido}
          onChange={(evento) => onApelidoChange(evento.target.value)}
          placeholder="Mari"
        />
      </label>

      <label className="field">
        <span>Confirmation Email</span>
        <input
          type="email"
          value={cadastro.email}
          onChange={(evento) => onEmailChange(evento.target.value)}
          placeholder="maria@exemplo.com"
          required
        />
      </label>

      <label className="field">
        <span>Start Date</span>
        <input
          type="date"
          value={cadastro.data_exercicio}
          onChange={(evento) => onDataExercicioChange(evento.target.value)}
          required
        />
      </label>

      <div className="field-grid">
        <label className="field">
          <span>Login</span>
          <input
            value={cadastro.login}
            onChange={(evento) => onLoginChange(evento.target.value)}
            placeholder="maria.silva"
            required
          />
        </label>

        <label className="field">
          <span>Password</span>
          <input
            type="password"
            value={cadastro.senha}
            onChange={(evento) => onSenhaChange(evento.target.value)}
            placeholder="********"
            minLength={6}
            required
          />
        </label>
      </div>

      <div className="actions">
        <button className="primary-button button--large" type="submit" disabled={carregando}>
          {carregando ? "Saving..." : "Create Account"}
        </button>
        <p className="helper">
          After registration, you will receive an email to confirm access.
        </p>
      </div>

      {mensagem ? <p className="success-box">{mensagem}</p> : null}
      {erro ? <p className="error-box">{erro}</p> : null}
    </form>
  )
}
