"use client"

import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { useEffect, useState } from "react"

import { CalendarioView } from "@/features/calendario/view/calendario-view"
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
import { useLanguage } from "@/shared/i18n/language-provider"

function formatarDataSegura(valor: string | null, idioma: "pt-BR" | "en") {
  if (!valor) {
    return "-"
  }

  const data = new Date(valor)
  if (Number.isNaN(data.getTime())) {
    return "-"
  }

  return new Intl.DateTimeFormat(idioma === "en" ? "en-US" : "pt-BR", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(data)
}

function formatarDataCurta(valor: string | null, idioma: "pt-BR" | "en") {
  return formatarDataSegura(valor, idioma)
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
  return formatarDataSegura(valor, idioma)
}

function limparTextoExibicao(valor: string | null | undefined) {
  const texto = valor?.trim()
  return texto && texto.length > 0 ? texto : "-"
}

type UsuarioPageControllerProps = {
  usuarioInicial: UsuarioConta | null
  historicoInicial: HistoricoFuncionalAnalise | null
  erroInicial: string | null
  modoDemo: boolean
}

type AbaDashboard = "perfil" | "historico" | "financeiro" | "calendario"

function normalizarAbaDashboard(valor: string | null, modoDemo: boolean): AbaDashboard {
  switch (valor) {
    case "historico":
    case "financeiro":
    case "calendario":
      return valor
    case "perfil":
      return "perfil"
    default:
      return modoDemo ? "historico" : "perfil"
  }
}

export function UsuarioPageController({
  usuarioInicial,
  historicoInicial,
  erroInicial,
  modoDemo,
}: UsuarioPageControllerProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { language, texts } = useLanguage()
  const [usuario, setUsuario] = useState<UsuarioConta | null>(usuarioInicial)
  const [abaAtiva, setAbaAtiva] = useState<AbaDashboard>(
    normalizarAbaDashboard(searchParams.get("aba"), modoDemo),
  )
  const [erro, setErro] = useState<string | null>(erroInicial)
  const [carregando, setCarregando] = useState(false)
  const [removendo, setRemovendo] = useState(false)
  const [saindo, setSaindo] = useState(false)
  const [indoParaCadastro, setIndoParaCadastro] = useState(false)
  const [historico, setHistorico] = useState<HistoricoFuncionalAnalise | null>(historicoInicial)
  const historicoExibido = historico ?? historicoInicial
  const nomeExibido = historicoExibido?.nome?.trim() || usuario?.nome || "-"
  const maspExibido = limparTextoExibicao(historicoExibido?.masp)
  const cargoExibido = limparTextoExibicao(historicoExibido?.cargo_atual)
  const simboloExibido = limparTextoExibicao(historicoExibido?.simbolo_atual)
  const dataNascimentoExibida = historicoExibido?.data_nascimento ?? null
  const dataPosseExibida = historicoExibido?.data_posse ?? null
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
      setUsuario((atual) => ({
        ...dados,
        nome: historicoExibido?.nome?.trim() ? historicoExibido.nome.trim() : dados.nome,
        data_exercicio: dados.data_exercicio ?? historicoExibido?.data_exercicio ?? atual?.data_exercicio ?? null,
      }))
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
    } finally {
      removerUsuarioAutenticadoId()
      setIndoParaCadastro(false)
      router.push("/")
    }
  }

  function selecionarAba(aba: AbaDashboard) {
    if (aba === "historico") {
      console.log("clicou história de carreira")
    }
    setAbaAtiva(aba)
    setErro(null)

    const params = new URLSearchParams(searchParams.toString())
    if (aba === "perfil") {
      params.delete("aba")
    } else {
      params.set("aba", aba)
    }

    const query = params.toString()
    router.replace(query ? `/usuario?${query}` : "/usuario", { scroll: false })
  }

  useEffect(() => {
    const abaDaUrl = normalizarAbaDashboard(searchParams.get("aba"), modoDemo)
    setAbaAtiva((atual) => (atual === abaDaUrl ? atual : abaDaUrl))
  }, [modoDemo, searchParams])

  useEffect(() => {
    console.log("activeTab:", abaAtiva)
  }, [abaAtiva])

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
              { key: "calendario" as const, label: language === "en" ? "Schedule" : "Escala" },
            ].map((aba) => (
              <button
                className={abaAtiva === aba.key ? "tab-button tab-button--active" : "tab-button"}
                key={aba.key}
                type="button"
                onClick={() => selecionarAba(aba.key)}
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

              {carregando && !usuario ? (
                <div className="empty-state">
                  <p>{texts.dashboard.loadingSessionData}</p>
                </div>
              ) : usuario ? (
                <>
                  {erro ? (
                    <div className="error-box" role="alert" style={{ marginBottom: "0.75rem" }}>
                      <p>{erro}</p>
                      <button
                        className="ghost-button ghost-button--compact"
                        type="button"
                        onClick={() => void recarregarUsuario()}
                      >
                        {texts.dashboard.tryAgain}
                      </button>
                    </div>
                  ) : null}
                  <div className="results-grid results-grid--profile">
                    <div className="result-block">
                      <span className="label">{texts.dashboard.fullName}</span>
                      <strong>{nomeExibido}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.dashboard.email}</span>
                      <strong>{usuario.email}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.dashboard.registrationNumber}</span>
                      <strong>{maspExibido}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.dashboard.birthDate}</span>
                      <strong>{formatarDataCurta(dataNascimentoExibida, language)}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.dashboard.possessionDate}</span>
                      <strong>{formatarDataCurta(dataPosseExibida, language)}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.registerForm.startDate}</span>
                      <strong>{formatarDataCurta(dataExercicioExibida, language)}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.dashboard.position}</span>
                      <strong>{cargoExibido}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.dashboard.symbol}</span>
                      <strong>{simboloExibido}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.dashboard.level}</span>
                      <strong>{nivelExibido}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">{texts.dashboard.grade}</span>
                      <strong>{grauExibido}</strong>
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
            <div style={{ padding: 24 }}>
              <h2>História de carreira carregou</h2>
              <p>Teste de renderização da aba.</p>
            </div>
          ) : abaAtiva === "calendario" ? (
            <CalendarioView modoDemo={modoDemo} />
          ) : (
            <FinanceiroView
              modoDemo={modoDemo}
              dataAposentadoriaPrevista={historicoExibido?.data_aposentadoria_prevista ?? null}
            />
          )}
        </section>
      </section>
    </main>
  )
}

