import type { FormEvent } from "react"

import type { UsuarioCadastro } from "../model/usuario.model"
import { useLanguage } from "@/shared/i18n/language-provider"

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
  const { texts } = useLanguage()

  return (
    <form className="card form-card form-card--register" onSubmit={onSubmit}>
      <div className="card-header card-header--tight">
        <div>
          <p className="eyebrow">{texts.registerForm.newUser}</p>
          <h2>{texts.registerForm.accessDetails}</h2>
        </div>
      </div>

      <label className="field">
        <span>{texts.registerForm.fullName}</span>
        <input
          value={cadastro.nome}
          onChange={(evento) => onNomeChange(evento.target.value)}
          placeholder="Maria Silva"
          required
        />
      </label>

      <label className="field">
        <span>{texts.registerForm.nickname}</span>
        <input
          value={cadastro.apelido}
          onChange={(evento) => onApelidoChange(evento.target.value)}
          placeholder="Mari"
        />
      </label>

      <label className="field">
        <span>{texts.registerForm.confirmationEmail}</span>
        <input
          type="email"
          value={cadastro.email}
          onChange={(evento) => onEmailChange(evento.target.value)}
          placeholder="maria@exemplo.com"
          required
        />
      </label>

      <label className="field">
        <span>{texts.registerForm.startDate}</span>
        <input
          type="date"
          value={cadastro.data_exercicio}
          onChange={(evento) => onDataExercicioChange(evento.target.value)}
          required
        />
      </label>

      <div className="field-grid">
        <label className="field">
          <span>{texts.registerForm.login}</span>
          <input
            value={cadastro.login}
            onChange={(evento) => onLoginChange(evento.target.value)}
            placeholder="maria.silva"
            required
          />
        </label>

        <label className="field">
          <span>{texts.registerForm.password}</span>
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
          {carregando ? texts.registerForm.saving : texts.registerForm.createAccount}
        </button>
        <p className="helper">{texts.registerForm.afterRegistration}</p>
      </div>

      {mensagem ? <p className="success-box">{mensagem}</p> : null}
      {erro ? <p className="error-box">{erro}</p> : null}
    </form>
  )
}
