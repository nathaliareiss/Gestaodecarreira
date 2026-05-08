"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState } from "react"

import type { HistoricoFuncionalAnalise } from "@/features/historico-funcional/model/historico-funcional.model"
import { HistoricoFuncionalView } from "@/features/historico-funcional/view/historico-funcional-view"
import { FinanceiroView } from "@/features/financeiro/view/financeiro-view"
import {
  carregarUsuarioAutenticado,
  encerrarSessao,
} from "@/features/auth/model/auth.repository"
import { type UsuarioConta } from "@/features/usuario/model/usuario.model"
import { removerUsuarioMaisRecente } from "@/features/usuario/model/usuario.repository"
import {
  removerSessaoDemo,
  removerUsuarioAutenticadoId,
} from "@/shared/auth/session"

function formatarDataCurta(valor: string | null) {
  if (!valor) {
    return "-"
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(valor))
}

function formatarDuracaoEmIngles(dias: number) {
  const anos = Math.floor(dias / 365)
  const meses = Math.floor((dias % 365) / 30)

  if (anos <= 0) {
    return `${meses}mo`
  }

  if (meses <= 0) {
    return `${anos}y`
  }

  return `${anos}y ${meses}mo`
}

function formatarDataEmIngles(valor: string | null) {
  if (!valor) {
    return "-"
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(valor))
}

type UsuarioPageControllerProps = {
  usuarioInicial: UsuarioConta | null
  historicoInicial: HistoricoFuncionalAnalise | null
  erroInicial: string | null
  modoDemo: boolean
}

export function UsuarioPageController({
  usuarioInicial,
  historicoInicial,
  erroInicial,
  modoDemo,
}: UsuarioPageControllerProps) {
  const router = useRouter()
  const [usuario, setUsuario] = useState<UsuarioConta | null>(usuarioInicial)
  const [abaAtiva, setAbaAtiva] = useState<"perfil" | "historico" | "financeiro">(
    modoDemo ? "historico" : "perfil",
  )
  const [erro, setErro] = useState<string | null>(erroInicial)
  const [carregando, setCarregando] = useState(false)
  const [removendo, setRemovendo] = useState(false)
  const [saindo, setSaindo] = useState(false)
  const [indoParaCadastro, setIndoParaCadastro] = useState(false)
  const dataExercicioExibida = usuario?.data_exercicio ?? historicoInicial?.data_exercicio ?? null
  const nivelExibido = historicoInicial?.nivel_atual ?? "-"
  const grauExibido = historicoInicial?.grau_atual ?? "-"
  const resumoDemo = historicoInicial?.resumo_grafico ?? null
  const rotuloSair = saindo ? "Exiting..." : modoDemo ? "Exit Demo" : "Exit"
  const indicadoresDemo = modoDemo && historicoInicial && resumoDemo ? [
    {
      label: "Years Worked",
      value: formatarDuracaoEmIngles(resumoDemo.tempo_trabalhado_dias),
    },
    {
      label: "Events",
      value: String(resumoDemo.eventos_totais),
    },
    {
      label: "Next Progression",
      value: formatarDataEmIngles(historicoInicial.proxima_progressao_prevista),
    },
    {
      label: "Retirement Estimate",
      value: formatarDataEmIngles(historicoInicial.data_aposentadoria_prevista),
    },
  ] : []

  async function recarregarUsuario() {
    setCarregando(true)
    setErro(null)

    try {
      const dados = await carregarUsuarioAutenticado()
      setUsuario(dados)
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao carregar.")
    } finally {
      setCarregando(false)
    }
  }

  async function excluirCadastro() {
    setRemovendo(true)
    setErro(null)

    try {
      await removerUsuarioMaisRecente()
      setUsuario(null)
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao remover.")
    } finally {
      setRemovendo(false)
    }
  }

  async function sair() {
    setSaindo(true)
    setErro(null)

    try {
      if (modoDemo) {
        removerSessaoDemo()
      } else {
        await encerrarSessao()
      }
    } catch {
      // Se a chamada remota falhar, a sessao local ainda pode ser encerrada.
    } finally {
      removerUsuarioAutenticadoId()
      setSaindo(false)
      router.push("/login")
    }
  }

  async function criarConta() {
    setIndoParaCadastro(true)
    setErro(null)

    try {
      if (modoDemo) {
        removerSessaoDemo()
      }
    } catch {
      // Se a limpeza local falhar, seguimos para a tela de cadastro.
    } finally {
      removerUsuarioAutenticadoId()
      setIndoParaCadastro(false)
      router.push("/")
    }
  }

  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--usuario-dashboard">
        <div className="hero-copy hero-copy--dashboard hero-copy--centered">
          <p className="eyebrow">CAREER DASHBOARD</p>
          <h1 className="hero-title--centered">CareerFlow</h1>
          <p className="hero-subtitle hero-subtitle--dashboard">Career Progression Analytics</p>
          {modoDemo ? <span className="status-pill">DEMO ACTIVE</span> : null}
        </div>
      </section>

      {indicadoresDemo.length > 0 ? (
        <section className="card hero-metrics" aria-label="Demo highlights">
          <div className="metric-strip metric-strip--hero">
            {indicadoresDemo.map((indicador) => (
              <div className="metric-line" key={indicador.label}>
                <span>{indicador.label}</span>
                <strong>{indicador.value}</strong>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      <section className="workbench workbench--single">
        <section className="card results-card">
          <div className="tab-bar">
            {[
              { key: "perfil" as const, label: "Profile" },
              { key: "historico" as const, label: "Career History" },
              { key: "financeiro" as const, label: "Finance" },
            ].map((aba) => (
              <button
                className={abaAtiva === aba.key ? "tab-button tab-button--active" : "tab-button"}
                key={aba.key}
                type="button"
                onClick={() => setAbaAtiva(aba.key)}
              >
                {aba.label}
              </button>
            ))}
            <button
              className="ghost-button ghost-button--compact tab-bar__action"
              type="button"
              onClick={() => void sair()}
              disabled={saindo}
            >
              {rotuloSair}
            </button>
          </div>

          {abaAtiva === "perfil" ? (
            <>
              <div className="card-header">
                <div>
                  <p className="eyebrow">PROFILE OVERVIEW</p>
                  <h2>Professional Profile</h2>
                </div>
                <span className="status-pill">
                  {usuario?.email_confirmado ? "Confirmed" : "Pending"}
                </span>
              </div>

              {carregando ? (
                <div className="empty-state">
                  <p>Loading session data...</p>
                </div>
              ) : erro ? (
                <div className="empty-state">
                  <p>{erro}</p>
                  <button
                    className="primary-button"
                    type="button"
                    onClick={() => void recarregarUsuario()}
                  >
                    Try again
                  </button>
                </div>
              ) : usuario ? (
                <>
                  <div className="results-grid">
                    <div className="result-block">
                      <span className="label">Full Name</span>
                      <strong>{usuario.nome}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Email</span>
                      <strong>{usuario.email}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Level</span>
                      <strong>{nivelExibido}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Grade</span>
                      <strong>{grauExibido}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Start Date</span>
                      <strong>{formatarDataCurta(dataExercicioExibida)}</strong>
                    </div>
                  </div>

                  <div className="actions">
                    <div className="actions-row">
                      {!modoDemo ? (
                        <button
                          className="ghost-button"
                          type="button"
                          onClick={() => void excluirCadastro()}
                          disabled={removendo}
                        >
                          {removendo ? "Removing..." : "Clear Last Record"}
                        </button>
                      ) : null}
                    </div>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <p>
                    No active session was found. Sign in again to view your data.
                  </p>
                  <Link className="primary-button" href="/login">
                    Go to Login
                  </Link>
                </div>
              )}
            </>
          ) : abaAtiva === "historico" ? (
            <HistoricoFuncionalView
              usuarioId={usuario?.id ?? null}
              historicoInicial={historicoInicial}
              modoDemo={modoDemo}
              onCreateAccount={() => void criarConta()}
              criandoConta={indoParaCadastro}
            />
          ) : (
            <FinanceiroView />
          )}
        </section>
      </section>
    </main>
  )
}

