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
  onLoginChange,
  onSenhaChange,
  onUsarExemplo,
}: UsuarioFormViewProps) {
  return (
    <form className="card form-card" onSubmit={onSubmit}>
      <div className="card-header">
        <div>
          <p className="eyebrow">Novo usuario</p>
          <h2>Dados de acesso</h2>
        </div>
        <button className="ghost-button" type="button" onClick={onUsarExemplo}>
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
        <span>Email</span>
        <input
          type="email"
          value={cadastro.email}
          onChange={(evento) => onEmailChange(evento.target.value)}
          placeholder="maria@exemplo.com"
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
        <button className="primary-button" type="submit" disabled={carregando}>
          {carregando ? "Salvando..." : "Cadastrar e ir para o usuario"}
        </button>
        <p className="helper">
          Depois do cadastro, a pessoa vai para <code>/usuario</code> e o email de
          confirmacao pode apontar para <code>/confirmar-email?token=...</code>.
        </p>
      </div>

      {erro ? <p className="error-box">{erro}</p> : null}
    </form>
  )
}
