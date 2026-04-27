"use client"

import type { FormEvent } from "react"

import type { CadastroCarreiraRequest } from "../carreira.types"

type CarreiraFormProps = {
  form: CadastroCarreiraRequest
  carregando: boolean
  erro: string | null
  onSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onNomeChange: (valor: string) => void
  onDataNascimentoChange: (valor: string) => void
  onDataIngressoChange: (valor: string) => void
  onCltChange: (valor: boolean) => void
  onUsarExemplo: () => void
}

export function CarreiraForm({
  form,
  carregando,
  erro,
  onSubmit,
  onNomeChange,
  onDataNascimentoChange,
  onDataIngressoChange,
  onCltChange,
  onUsarExemplo,
}: CarreiraFormProps) {
  return (
    <form className="card form-card" onSubmit={onSubmit}>
      <div className="card-header">
        <div>
          <p className="eyebrow">Cadastro</p>
          <h2>Entrada de dados</h2>
        </div>
        <button className="ghost-button" type="button" onClick={onUsarExemplo}>
          Usar exemplo
        </button>
      </div>

      <label className="field">
        <span>Nome</span>
        <input
          value={form.nome}
          onChange={(evento) => onNomeChange(evento.target.value)}
          placeholder="Maria"
          required
        />
      </label>

      <div className="field-grid">
        <label className="field">
          <span>Data de nascimento</span>
          <input
            type="date"
            value={form.data_nascimento}
            onChange={(evento) => onDataNascimentoChange(evento.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>Data de ingresso</span>
          <input
            type="date"
            value={form.data_ingresso}
            onChange={(evento) => onDataIngressoChange(evento.target.value)}
            required
          />
        </label>
      </div>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.tem_tempo_clt_averbado}
          onChange={(evento) => onCltChange(evento.target.checked)}
        />
        <span>Tem tempo CLT averbado</span>
      </label>

      <div className="actions">
        <button className="primary-button" type="submit" disabled={carregando}>
          {carregando ? "Calculando..." : "Calcular resumo"}
        </button>
        <p className="helper">
          Front: <code>{process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}</code>
        </p>
      </div>

      {erro ? <p className="error-box">{erro}</p> : null}
    </form>
  )
}

