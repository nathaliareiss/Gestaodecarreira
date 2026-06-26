"use client"

import Link from "next/link"
import { useEffect } from "react"

export default function UsuarioError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--usuario-dashboard">
        <div className="hero-copy hero-copy--dashboard hero-copy--centered">
          <p className="eyebrow">CAREER DASHBOARD</p>
          <h1 className="hero-title--centered">CareerFlow</h1>
          <p className="hero-subtitle hero-subtitle--dashboard">
            Não foi possível abrir esta área agora.
          </p>
        </div>
      </section>

      <section className="workbench workbench--single">
        <section className="card results-card">
          <div className="empty-state">
            <p>A aba História de carreira encontrou um problema ao carregar.</p>
            <p>Tente novamente ou volte para a página anterior.</p>
            <div className="actions-row">
              <button className="primary-button" type="button" onClick={reset}>
                Tentar novamente
              </button>
              <Link className="ghost-button" href="/usuario?aba=perfil">
                Voltar ao perfil
              </Link>
            </div>
          </div>
        </section>
      </section>
    </main>
  )
}
