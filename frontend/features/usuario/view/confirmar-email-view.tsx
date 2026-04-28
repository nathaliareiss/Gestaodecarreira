"use client"

import Link from "next/link"
import { useEffect, useState } from "react"

import type { UsuarioConta } from "../model/usuario.model"
import { confirmarUsuarioPorToken } from "../model/usuario.storage"

type ConfirmarEmailViewProps = {
  token: string | null
}

export function ConfirmarEmailView({ token }: ConfirmarEmailViewProps) {
  const [usuario, setUsuario] = useState<UsuarioConta | null>(null)
  const [erro, setErro] = useState<string | null>(null)

  useEffect(() => {
    const timer = window.setTimeout(() => {
      if (!token) {
        setErro("Token de confirmacao ausente.")
        return
      }

      const confirmado = confirmarUsuarioPorToken(token)
      if (!confirmado) {
        setErro("Nao foi possivel confirmar este email.")
        return
      }

      setUsuario(confirmado)
      setErro(null)
    }, 0)

    return () => window.clearTimeout(timer)
  }, [token])

  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Confirmacao de email</p>
          <h1>Valide o acesso com um clique no link do email.</h1>
          <p className="hero-text">
            Esta rota e o destino do link de confirmacao que voce envia por email.
          </p>
        </div>

        <div className="hero-grid">
          <article className="mini-card">
            <h2>Status</h2>
            <p>{usuario ? "Email confirmado" : erro ?? "Processando"}</p>
          </article>
          <article className="mini-card">
            <h2>Proxima etapa</h2>
            <p>Voltar para a pagina do usuario e conferir os dados salvos.</p>
          </article>
        </div>
      </section>

      <section className="workbench">
        <section className="card results-card">
          <div className="card-header">
            <div>
              <p className="eyebrow">Resultado</p>
              <h2>Confirmacao finalizada</h2>
            </div>
            <span className="status-pill">{usuario ? "ok" : "pendente"}</span>
          </div>

          {usuario ? (
            <div className="empty-state">
              <p>
                O email de <strong>{usuario.email}</strong> foi confirmado com sucesso.
              </p>
              <Link className="primary-button" href="/usuario">
                Ir para a pagina do usuario
              </Link>
            </div>
          ) : (
            <div className="empty-state">
              <p>{erro ?? "Aguardando confirmacao..."}</p>
              <Link className="primary-button" href="/usuario">
                Voltar para o usuario
              </Link>
            </div>
          )}
        </section>

        <aside className="note-card">
          <p className="eyebrow">Como usar</p>
          <h2>Quando a API chegar, mande este link no email</h2>
          <p>
            O template do email deve apontar para <code>/confirmar-email?token=...</code>.
          </p>
          <p>
            Resend e Brevo sao as duas opcoes gratuitas mais praticas para esse tipo de
            fluxo.
          </p>
        </aside>
      </section>
    </main>
  )
}
