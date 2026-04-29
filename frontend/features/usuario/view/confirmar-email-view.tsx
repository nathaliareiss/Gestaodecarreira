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
        setErro("Token de confirmação ausente.")
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
        setErro(error instanceof Error ? error.message : "Não foi possível confirmar este e-mail.")
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
          <p className="eyebrow">Confirmação de e-mail</p>
          <h1>Valide o acesso com um clique no link do email.</h1>
         
        </div>

        <div className="hero-grid">
          <article className="mini-card">
            <h2>Status</h2>
            <p>{carregando ? "Processando" : usuario ? "E-mail confirmado" : erro ?? "Pendente"}</p>
          </article>
          <article className="mini-card">
            <h2>Próxima etapa</h2>
            <p>Voltar para a página do usuário e conferir os dados salvos.</p>
          </article>
        </div>
      </section>

      <section className="workbench">
        <section className="card results-card">
          <div className="card-header">
            <div>
              <p className="eyebrow">Resultado</p>
              <h2>Confirmação finalizada</h2>
            </div>
            <span className="status-pill">{usuario ? "ok" : "pendente"}</span>
          </div>

          {carregando ? (
            <div className="empty-state">
              <p>Confirmando usuário...</p>
            </div>
          ) : usuario ? (
            <div className="empty-state">
              <p>
                O e-mail de <strong>{usuario.email}</strong> foi confirmado com sucesso.
              </p>
              <Link className="primary-button" href="/usuario">
                Ir para a página do usuário
              </Link>
            </div>
          ) : (
            <div className="empty-state">
              <p>{erro ?? "Aguardando confirmação..."}</p>
              <Link className="primary-button" href="/usuario">
                Voltar para o usuário
              </Link>
            </div>
          )}
        </section>

      
      </section>
    </main>
  )
}
