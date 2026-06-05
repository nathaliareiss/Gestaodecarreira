"use client"

import Link from "next/link"
import type { FormEvent } from "react"
import { useState } from "react"

import type { UsuarioCadastro } from "../model/usuario.model"
import type { CadastroErroMensagem } from "../controller/use-usuario-controller"
import { useLanguage } from "@/shared/i18n/language-provider"

type UsuarioFormViewProps = {
  cadastro: UsuarioCadastro
  carregando: boolean
  erro: CadastroErroMensagem | null
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
  const [senhaVisivel, setSenhaVisivel] = useState(false)

  return (
    <form className="card form-card form-card--register" onSubmit={onSubmit} autoComplete="off">
      <div className="card-header card-header--tight">
        <div>
          <p className="eyebrow">{texts.registerForm.newUser}</p>
          <h2>{texts.registerForm.accessDetails}</h2>
        </div>
      </div>

      <label className="field">
        <span>{texts.registerForm.fullName}</span>
        <input
          autoComplete="off"
          value={cadastro.nome}
          onChange={(evento) => onNomeChange(evento.target.value)}
          required
        />
      </label>

      <label className="field">
        <span>{texts.registerForm.nickname}</span>
        <input
          autoComplete="off"
          value={cadastro.apelido}
          onChange={(evento) => onApelidoChange(evento.target.value)}
        />
      </label>

      <label className="field">
        <span>{texts.registerForm.confirmationEmail}</span>
        <input
          type="email"
          autoComplete="off"
          value={cadastro.email}
          onChange={(evento) => onEmailChange(evento.target.value)}
          required
        />
      </label>

      <label className="field">
        <span>{texts.registerForm.startDate}</span>
        <input
          type="date"
          autoComplete="off"
          value={cadastro.data_exercicio}
          onChange={(evento) => onDataExercicioChange(evento.target.value)}
          required
        />
      </label>

      <div className="field-grid">
        <label className="field">
          <span>{texts.registerForm.login}</span>
          <input
            autoComplete="off"
            value={cadastro.login}
            onChange={(evento) => onLoginChange(evento.target.value)}
            required
          />
        </label>

        <label className="field">
          <span>{texts.registerForm.password}</span>
          <div className="password-field">
            <input
              type={senhaVisivel ? "text" : "password"}
              autoComplete="new-password"
              value={cadastro.senha}
              onChange={(evento) => onSenhaChange(evento.target.value)}
              minLength={6}
              required
            />
            <button
              className="password-field__toggle"
              type="button"
              onClick={() => setSenhaVisivel((atual) => !atual)}
              aria-pressed={senhaVisivel}
              aria-label={senhaVisivel ? "Ocultar senha" : "Mostrar senha"}
              title={senhaVisivel ? "Ocultar senha" : "Mostrar senha"}
            >
              {senhaVisivel ? (
                <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                  <path
                    d="M2 12s3.5-7 10-7c1.7 0 3.1.4 4.4 1.1"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <path
                    d="M22 12s-3.5 7-10 7c-1.7 0-3.1-.4-4.4-1.1"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="3"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  />
                  <path
                    d="M3 3l18 18"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                  <path
                    d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinejoin="round"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="3"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  />
                </svg>
              )}
            </button>
          </div>
        </label>
      </div>

      <div className="actions">
        <button className="primary-button button--large" type="submit" disabled={carregando}>
          {carregando ? texts.registerForm.saving : texts.registerForm.createAccount}
        </button>
        <p className="helper">{texts.registerForm.afterRegistration}</p>
      </div>

      {mensagem ? <p className="success-box">{mensagem}</p> : null}
      {erro ? (
        <p className="error-box">
          <span>{erro.message}</span>
          {erro.action ? (
            <>
              {" "}
              <Link className="error-box__link" href={erro.action.href}>
                {erro.action.label}
              </Link>
            </>
          ) : null}
        </p>
      ) : null}
    </form>
  )
}
