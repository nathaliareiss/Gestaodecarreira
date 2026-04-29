import type { FormEvent } from "react"

import type { UsuarioCadastro } from "../model/usuario.model"

type UsuarioFormViewProps = {
  cadastro: UsuarioCadastro
  carregando: boolean
  erro: string | null
  onSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onNomeChange: (valor: string) => void
  onApelidoChange: (valor: string) => void
  onEmailChange: (valor: string) => void
  onDataExercicioChange: (valor: string) => void
  onLoginChange: (valor: string) => void
  onSenhaChange: (valor: string) => void
  onUsarExemplo: () => void
}

export function UsuarioFormView({
  cadastro,
  carregando,
  erro,
  onSubmit,
  onNomeChange,
  onApelidoChange,
  onEmailChange,
  onDataExercicioChange,
  onLoginChange,
  onSenhaChange,
  onUsarExemplo,
}: UsuarioFormViewProps) {
  return (
    <form className="card form-card form-card--register" onSubmit={onSubmit}>
      <div className="card-header card-header--tight">
        <div>
          <p className="eyebrow">Novo usuário</p>
          <h2>Dados de acesso</h2>
        </div>
        <button
          className="ghost-button ghost-button--compact"
          type="button"
          onClick={onUsarExemplo}
        >
          Usar exemplo
        </button>
      </div>

      <label className="field">
        <span>Nome completo</span>
        <input
          value={cadastro.nome}
          onChange={(evento) => onNomeChange(evento.target.value)}
          placeholder="Maria Silva"
          required
        />
      </label>

      <label className="field">
        <span>Apelido (opcional)</span>
        <input
          value={cadastro.apelido}
          onChange={(evento) => onApelidoChange(evento.target.value)}
          placeholder="Mari"
        />
      </label>

      <label className="field">
        <span>E-mail para confirmação</span>
        <input
          type="email"
          value={cadastro.email}
          onChange={(evento) => onEmailChange(evento.target.value)}
          placeholder="maria@exemplo.com"
          required
        />
      </label>

      <label className="field">
        <span>Data de exercício</span>
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
          <span>Senha</span>
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
          {carregando ? "Salvando..." : "Cadastrar e ir para o usuário"}
        </button>
        <p className="helper">
          Depois do cadastro, você vai receber um e-mail para confirmar o acesso.
        </p>
      </div>

      {erro ? <p className="error-box">{erro}</p> : null}
    </form>
  )
}
