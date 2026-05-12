"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

import { LoginController } from "./login-controller"
import { limparSessaoAutenticada } from "../model/auth-session"
import { carregarUsuarioAutenticado } from "../model/auth.repository"
import { ApiResponseError } from "@/shared/api/client"

function TelaVerificacaoLogin() {
  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--usuario-dashboard">
        <div className="hero-copy hero-copy--dashboard hero-copy--centered">
          <p className="eyebrow">CAREERFLOW</p>
          <h1 className="hero-title--centered">Login</h1>
          <p className="hero-subtitle hero-subtitle--dashboard">Checking your session...</p>
        </div>
      </section>

      <section className="workbench workbench--single">
        <section className="card results-card">
          <div className="empty-state">
            <p>Validating access...</p>
          </div>
        </section>
      </section>
    </main>
  )
}

export function LoginAccessGate() {
  const router = useRouter()
  const [verificando, setVerificando] = useState(true)

  useEffect(() => {
    let ativo = true

    async function validarSessao() {
      try {
        await carregarUsuarioAutenticado()

        if (!ativo) {
          return
        }

        router.replace("/usuario")
      } catch (error) {
        if (error instanceof ApiResponseError && error.status === 401) {
          await limparSessaoAutenticada()
        }
      } finally {
        if (ativo) {
          setVerificando(false)
        }
      }
    }

    void validarSessao()

    return () => {
      ativo = false
    }
  }, [router])

  if (verificando) {
    return <TelaVerificacaoLogin />
  }

  return <LoginController />
}
