"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"

import type { HistoricoFuncionalAnalise } from "@/features/historico-funcional/model/historico-funcional.model"
import { buscarUltimoHistoricoFuncional } from "@/features/historico-funcional/model/historico-funcional.repository"
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
import { useLanguage } from "@/shared/i18n/language-provider"

function formatarDataCurta(valor: string | null, idioma: "pt-BR" | "en") {
  if (!valor) {
    return "-"
  }

  return new Intl.DateTimeFormat(idioma === "en" ? "en-US" : "pt-BR", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(valor))
}

function formatarDuracaoEmIngles(dias: number, idioma: "pt-BR" | "en") {
  const anos = Math.floor(dias / 365)
  const meses = Math.floor((dias % 365) / 30)

  if (anos <= 0) {
    return idioma === "en" ? `${meses}mo` : `${meses}m`
  }

  if (meses <= 0) {
    return idioma === "en" ? `${anos}y` : `${anos}a`
  }

  return idioma === "en" ? `${anos}y ${meses}mo` : `${anos}a ${meses}m`
}

function formatarDataEmIngles(valor: string | null, idioma: "pt-BR" | "en") {
  if (!valor) {
    return "-"
  }

  return new Intl.DateTimeFormat(idioma === "en" ? "en-US" : "pt-BR", {
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
  const { language, texts } = useLanguage()
  const [usuario, setUsuario] = useState<UsuarioConta | null>(usuarioInicial)
  const [abaAtiva, setAbaAtiva] = useState<"perfil" | "historico" | "financeiro">(
    modoDemo ? "historico" : "perfil",
  )
  const [erro, setErro] = useState<string | null>(erroInicial)
  const [carregando, setCarregando] = useState(false)
  const [removendo, setRemovendo] = useState(false)
  const [saindo, setSaindo] = useState(false)
  const [indoParaCadastro, setIndoParaCadastro] = useState(false)
  const [historico, setHistorico] = useState<HistoricoFuncionalAnalise | null>(historicoInicial)
  const [carregandoHistorico, setCarregandoHistorico] = useState(false)
  const historicoExibido = historico ?? historicoInicial
  const dataExercicioExibida = usuario?.data_exercicio ?? historicoExibido?.data_exercicio ?? null
  const nivelExibido = historicoExibido?.nivel_atual ?? "-"
  const grauExibido = historicoExibido?.grau_atual ?? "-"
  const resumoDemo = historicoExibido?.resumo_grafico ?? null
  const rotuloSair = saindo ? texts.dashboard.exitLabel : modoDemo ? texts.dashboard.exitDemo : texts.dashboard.exit
  const indicadoresDemo = modoDemo && historicoExibido && resumoDemo ? [
    {
      label: texts.dashboard.yearsWorked,
      value: formatarDuracaoEmIngles(resumoDemo.tempo_trabalhado_dias, language),
    },
    {
      label: texts.dashboard.events,
      value: String(resumoDemo.eventos_totais),
    },
    {
      label: texts.dashboard.nextProgression,
      value: formatarDataEmIngles(historicoExibido.proxima_progressao_prevista, language),
    },
    {
      label: texts.dashboard.retirementEstimate,
      value: formatarDataEmIngles(historicoExibido.data_aposentadoria_prevista, language),
    },
  ] : []

  async function recarregarUsuario() {
    setCarregando(true)
    setErro(null)

    try {
      const dados = await carregarUsuarioAutenticado()
      setUsuario(dados)
    } catch (error) {
      setErro(error instanceof Error ? error.message : (language === "en" ? "Unexpected failure while loading." : "Falha inesperada ao carregar."))
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
      setErro(error instanceof Error ? error.message : (language === "en" ? "Unexpected failure while removing." : "Falha inesperada ao remover."))
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

  useEffect(() => {
    if (modoDemo || abaAtiva !== "perfil" || !usuario?.id) {
      return
    }

    let ativo = true
    setCarregandoHistorico(true)

    void (async () => {
      try {
        const ultimoHistorico = await buscarUltimoHistoricoFuncional(usuario.id)
        if (ativo) {
          setHistorico(ultimoHistorico)
        }
      } catch {
        if (ativo) {
          setHistorico(null)
        }
      } finally {
        if (ativo) {
          setCarregandoHistorico(false)
        }
      }
    })()

    return () => {
      ativo = false
    }
  }, [abaAtiva, modoDemo, usuario?.id])

  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--usuario-dashboard">
        <div className="hero-copy hero-copy--dashboard hero-copy--centered">
          <p className="eyebrow">{texts.dashboard.careerDashboard.toUpperCase()}</p>
          <h1 className="hero-title--centered">CareerFlow</h1>
          <p className="hero-subtitle hero-subtitle--dashboard">
            {texts.dashboard.careerProgressionAnalytics}
          </p>
          {modoDemo ? <span className="status-pill">{texts.dashboard.demoActive}</span> : null}
        </div>
      </section>

      {indicadoresDemo.length > 0 ? (
        <section className="card hero-metrics" aria-label={texts.dashboard.demoHighlights}>
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
              { key: "perfil" as const, label: texts.dashboard.profile },
              { key: "historico" as const, label: texts.dashboard.history },
              { key: "financeiro" as const, label: texts.dashboard.finance },
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
                  <p className="eyebrow">{texts.dashboard.profileOverview.toUpperCase()}</p>
                  <h2>{texts.dashboard.professionalProfile}</h2>
                </div>
                <span className="status-pill">
                  {usuario?.email_confirmado ? texts.dashboard.confirmed : texts.dashboard.pending}
                </span>
              </div>

              {carregando || carregandoHistorico ? (
                <div className="empty-state">
                  <p>{texts.dashboard.loadingSessionData}</p>
                </div>
              ) : erro ? (
                <div className="empty-state">
                  <p>{erro}</p>
                  <button
                    className="primary-button"
                    type="button"
                    onClick={() => void recarregarUsuario()}
                  >
                    {texts.dashboard.tryAgain}
                  </button>
                </div>
              ) : usuario ? (
                <>
                  <div className="results-grid">
                    <div className="result-block">
                      <span className="label">{texts.registerForm.fullName}</span>
                      <strong>{usuario.nome}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.dashboard.email}</span>
                      <strong>{usuario.email}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.dashboard.level}</span>
                      <strong>{nivelExibido}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.dashboard.grade}</span>
                      <strong>{grauExibido}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.registerForm.startDate}</span>
                      <strong>{formatarDataCurta(dataExercicioExibida, language)}</strong>
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
                          {removendo ? texts.dashboard.loading : texts.dashboard.removeLastRecord}
                        </button>
                      ) : null}
                    </div>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <p>{texts.dashboard.noSession}</p>
                  <Link className="primary-button" href="/login">
                    {texts.dashboard.goToLogin}
                  </Link>
                </div>
              )}
            </>
          ) : abaAtiva === "historico" ? (
            <HistoricoFuncionalView
              usuarioId={usuario?.id ?? null}
              historicoInicial={historicoExibido}
              modoDemo={modoDemo}
              onCreateAccount={() => void criarConta()}
              criandoConta={indoParaCadastro}
            />
          ) : (
            <FinanceiroView modoDemo={modoDemo} />
          )}
        </section>
      </section>
    </main>
  )
}

