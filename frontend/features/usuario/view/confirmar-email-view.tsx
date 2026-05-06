"use client"

import Link from "next/link"
import { useEffect, useState } from "react"

import type { UsuarioConta } from "../model/usuario.model"
import { confirmarUsuarioPorToken } from "../model/usuario.repository"

type ConfirmarEmailViewProps = {
  token: string | null
}

export function ConfirmarEmailView({ token }: ConfirmarEmailViewProps) {
  const [usuario, setUsuario] = useState<UsuarioConta | null>(null)
  const [erro, setErro] = useState<string | null>(null)
  const [carregando, setCarregando] = useState(true)

  useEffect(() => {
    let ativo = true

    async function confirmar() {
      if (!token) {
        setErro("Missing token.")
        setCarregando(false)
        return
      }

      try {
        const confirmado = await confirmarUsuarioPorToken(token)
        if (!ativo) {
          return
        }

        setUsuario(confirmado)
        setErro(null)
      } catch (error) {
        if (!ativo) {
          return
        }

        setUsuario(null)
        setErro(error instanceof Error ? error.message : "Unable to confirm this email.")
      } finally {
        if (ativo) {
          setCarregando(false)
        }
      }
    }

    void confirmar()

    return () => {
      ativo = false
    }
  }, [token])

  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Email Confirmation</p>
          <h1>Validate access with one click on the email link.</h1>
        </div>

        <div className="hero-grid">
          <article className="mini-card">
            <h2>Status</h2>
            <p>{carregando ? "Processing" : usuario ? "Email confirmed" : erro ?? "Pending"}</p>
          </article>
          <article className="mini-card">
            <h2>Next Step</h2>
            <p>Return to the user page and review the saved data.</p>
          </article>
        </div>
      </section>

      <section className="workbench">
        <section className="card results-card">
          <div className="card-header">
            <div>
              <p className="eyebrow">Result</p>
              <h2>Confirmation Complete</h2>
            </div>
            <span className="status-pill">{usuario ? "OK" : "Pending"}</span>
          </div>

          {carregando ? (
            <div className="empty-state">
              <p>Confirming user...</p>
            </div>
          ) : usuario ? (
            <div className="empty-state">
              <p>
                The email <strong>{usuario.email}</strong> was confirmed successfully.
              </p>
              <Link className="primary-button" href="/usuario">
                Go to User Page
              </Link>
            </div>
          ) : (
            <div className="empty-state">
              <p>{erro ?? "Waiting for confirmation..."}</p>
              <Link className="primary-button" href="/usuario">
                Back to User Page
              </Link>
            </div>
          )}
        </section>
      </section>
    </main>
  )
}
