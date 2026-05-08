"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

import { carregarUsuarioAutenticado } from "@/features/auth/model/auth.repository"
import type { HistoricoFuncionalAnalise } from "@/features/historico-funcional/model/historico-funcional.model"
import { UsuarioPageController } from "@/features/usuario/controller/usuario-page-controller"
import type { UsuarioConta } from "@/features/usuario/model/usuario.model"
import { DEMO_HISTORICO, DEMO_USUARIO } from "@/shared/demo/demo-data"
import {
  modoDemoAtivoNoCliente,
  salvarSessaoDemo,
} from "@/shared/auth/session"

type EstadoTela =
  | {
      status: "loading"
    }
  | {
      status: "ready"
      usuario: UsuarioConta
      historico: HistoricoFuncionalAnalise | null
      modoDemo: boolean
    }

function TelaCarregamento() {
  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--usuario-dashboard">
        <div className="hero-copy hero-copy--dashboard hero-copy--centered">
          <p className="eyebrow">CAREER DASHBOARD</p>
          <h1 className="hero-title--centered">CareerFlow</h1>
          <p className="hero-subtitle hero-subtitle--dashboard">Preparing your session...</p>
        </div>
      </section>

      <section className="workbench workbench--single">
        <section className="card results-card">
          <div className="empty-state">
            <p>Loading dashboard...</p>
          </div>
        </section>
      </section>
    </main>
  )
}

export function UsuarioAccessGate() {
  const router = useRouter()
  const [estado, setEstado] = useState<EstadoTela>({ status: "loading" })

  useEffect(() => {
    let ativo = true

    async function carregarSessao() {
      const demoAtivo = modoDemoAtivoNoCliente()

      if (demoAtivo) {
        salvarSessaoDemo(DEMO_USUARIO.id)
        if (!ativo) {
          return
        }

        setEstado({
          status: "ready",
          usuario: DEMO_USUARIO,
          historico: DEMO_HISTORICO,
          modoDemo: true,
        })
        return
      }

      try {
        const usuario = await carregarUsuarioAutenticado()

        if (!ativo) {
          return
        }

        setEstado({
          status: "ready",
          usuario,
          historico: null,
          modoDemo: false,
        })
      } catch {
        router.replace("/")
      }
    }

    void carregarSessao()

    return () => {
      ativo = false
    }
  }, [router])

  if (estado.status === "loading") {
    return <TelaCarregamento />
  }

  return (
    <UsuarioPageController
      usuarioInicial={estado.usuario}
      historicoInicial={estado.historico}
      erroInicial={null}
      modoDemo={estado.modoDemo}
    />
  )
}
