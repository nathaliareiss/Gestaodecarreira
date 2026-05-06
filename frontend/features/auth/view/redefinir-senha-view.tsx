"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import type { FormEvent } from "react"
import { useState } from "react"

import { redefinirSenhaUsuario } from "../model/auth.repository"

type RedefinirSenhaViewProps = {
  token: string | null
}

export function RedefinirSenhaView({ token }: RedefinirSenhaViewProps) {
  const router = useRouter()
  const [novaSenha, setNovaSenha] = useState("")
  const [confirmarSenha, setConfirmarSenha] = useState("")
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [sucesso, setSucesso] = useState<string | null>(null)

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setCarregando(true)
    setErro(null)
    setSucesso(null)

    try {
      if (!token) {
        throw new Error("Missing token.")
      }

      if (novaSenha !== confirmarSenha) {
        throw new Error("Passwords do not match.")
      }

      const resposta = await redefinirSenhaUsuario({
        token,
        nova_senha: novaSenha,
      })

      setSucesso(resposta.message)
      setNovaSenha("")
      setConfirmarSenha("")
      router.push("/login")
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Unable to update the password.")
    } finally {
      setCarregando(false)
    }
  }

  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--login">
        <div className="hero-copy hero-copy--login">
          <p className="eyebrow">Reset Password</p>
          <h1>Create a new password to access your account.</h1>
          <p className="hero-text">
            Use the link you received by email to set a new password securely.
          </p>
        </div>

        <div className="login-panel">
          <form className="card form-card form-card--recovery" onSubmit={enviar}>
            <div className="card-header card-header--tight">
              <div>
                <p className="eyebrow">New Password</p>
                <h2>Update Access</h2>
              </div>
            </div>

            <label className="field">
              <span>New Password</span>
              <input
                type="password"
                value={novaSenha}
                onChange={(evento) => setNovaSenha(evento.target.value)}
                placeholder="********"
                autoComplete="new-password"
                minLength={6}
                required
              />
            </label>

            <label className="field">
              <span>Confirm Password</span>
              <input
                type="password"
                value={confirmarSenha}
                onChange={(evento) => setConfirmarSenha(evento.target.value)}
                placeholder="********"
                autoComplete="new-password"
                minLength={6}
                required
              />
            </label>

            <div className="actions actions--compact">
              <button className="primary-button button--large" type="submit" disabled={carregando}>
                {carregando ? "Updating..." : "Reset Password"}
              </button>
              <Link className="ghost-button ghost-button--compact" href="/login">
                Back to Sign In
              </Link>
            </div>

            {sucesso ? <p className="success-box">{sucesso}</p> : null}
            {erro ? <p className="error-box">{erro}</p> : null}
            {!token ? <p className="error-box">Missing token.</p> : null}
          </form>
        </div>
      </section>
    </main>
  )
}
