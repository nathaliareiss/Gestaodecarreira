"use client"

import { useCallback, useEffect, useState, type ChangeEvent, type FormEvent } from "react"

import { useLanguage } from "@/shared/i18n/language-provider"
import { ApiResponseError } from "@/shared/api/client"
import {
  acompanharLoteFinanceiro,
  calcularProgressoLote,
  formatarStatusLote,
  isBatchTerminalStatus,
} from "../model/financeiro-batch.mjs"
import {
  obterContrachequesSalvos,
  obterEvolucaoSalarialPersistida,
  criarImportacaoTemporariaFinanceiro,
  enviarLoteContracheques,
  obterStatusLoteFinanceiro,
} from "../model/financeiro.repository"
import type {
  FinanceiroContrachequeResumo,
  FinanceiroBatchStatusResponse,
  FinanceiroEvolucaoSalarialResponse,
  FinanceiroImportacaoTemporariaCriacaoResponse,
} from "../model/financeiro.model"
import {
  DEMO_FINANCEIRO_CONTRACHEQUES,
  DEMO_FINANCEIRO_EVOLUCAO,
} from "@/shared/demo/demo-data"
import type { SiteLanguage } from "@/shared/i18n/messages"

type FinanceTexts = (typeof import("@/shared/i18n/messages").LOCALE_TEXTS)["pt-BR"]["finance"]

const INTERVALO_POLLING_MS = 2000
const CAMINHO_DOWNLOAD_ASSISTENTE = "/downloads/gestao-de-carreira-assistente.exe"
const NOME_DOWNLOAD_ASSISTENTE = "GestaoDeCarreira-Assistente.exe"

type FinanceiroViewProps = {
  modoDemo: boolean
}

function listaSegura<T>(valor: T[] | null | undefined): T[] {
  return Array.isArray(valor) ? valor : []
}

function mapaNumericoSegura(valor: Record<string, number> | null | undefined): Record<string, number> {
  if (!valor || typeof valor !== "object" || Array.isArray(valor)) {
    return {}
  }

  return Object.fromEntries(
    Object.entries(valor).map(([chave, item]) => {
      const numero = typeof item === "number" ? item : Number(item)
      return [chave, Number.isFinite(numero) ? numero : 0]
    }),
  )
}

function formatarErroFinanceiro(
  error: unknown,
  idioma: SiteLanguage,
  contexto: "analise" | "lote" | "importacao" | "envio",
  textosFinanceiro?: Pick<FinanceTexts, "assistantLaunchError">,
) {
  if (contexto === "importacao") {
    return (
      textosFinanceiro?.assistantLaunchError ??
      (idioma === "en"
        ? "We could not start the import right now. Please try again or check if the assistant is open."
        : "Não foi possível iniciar a importação agora. Tente novamente ou verifique se o assistente está aberto.")
    )
  }

  if (error instanceof ApiResponseError) {
    if (error.status === 401) {
      return idioma === "en"
        ? "Your session expired. Please sign in again to continue."
        : "Sua sessão expirou. Entre novamente para continuar."
    }

    if (error.status === 404) {
      if (contexto === "analise") {
        return idioma === "en"
          ? "No saved payroll analysis is available yet."
          : "Ainda não há análise salarial salva."
      }

      if (contexto === "lote") {
        return idioma === "en"
          ? "The payroll batch was not found."
          : "O lote financeiro não foi encontrado."
      }

      if (contexto === "importacao") {
        return idioma === "en"
          ? "The import assistant is no longer available."
          : "O assistente de importação não está mais disponível."
      }
    }

    if (error.status === 500) {
      return idioma === "en"
        ? "The Finance area is temporarily unavailable. Please try again in a moment."
        : "O Financeiro está temporariamente indisponível. Tente novamente em instantes."
    }

    return error.message
  }

  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message
  }

  return idioma === "en"
    ? "We could not complete this action right now."
    : "Não foi possível concluir essa ação agora."
}

function formatarTamanhoArquivo(bytes: number) {
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return "-"
  }

  if (bytes < 1024) {
    return `${bytes} B`
  }

  const kilobytes = bytes / 1024
  if (kilobytes < 1024) {
    return `${kilobytes.toFixed(1)} KB`
  }

  return `${(kilobytes / 1024).toFixed(1)} MB`
}

const formatadorMoeda = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

function formatarMoeda(valor: number | null) {
  if (valor == null || !Number.isFinite(valor)) {
    return "-"
  }

  return formatadorMoeda.format(valor)
}

function formatarVariacaoPercentual(valor: number | null, idioma: SiteLanguage) {
  if (valor == null || !Number.isFinite(valor)) {
    return idioma === "en" ? "Base year" : "Ano base"
  }

  const sinal = valor > 0 ? "+" : ""
  return `${sinal}${valor.toFixed(2)}%`
}

async function copiarTextoParaClipboard(texto: string) {
  if (!texto) {
    return false
  }

  if (navigator?.clipboard?.writeText) {
    await navigator.clipboard.writeText(texto)
    return true
  }

  return false
}

async function verificarDisponibilidadeAssistente() {
  try {
    const response = await fetch(CAMINHO_DOWNLOAD_ASSISTENTE, {
      method: "HEAD",
      cache: "no-store",
    })

    return response.ok
  } catch {
    return false
  }
}

function iniciarDownloadAssistente() {
  const link = document.createElement("a")
  link.href = CAMINHO_DOWNLOAD_ASSISTENTE
  link.download = NOME_DOWNLOAD_ASSISTENTE
  link.rel = "noopener"
  document.body.appendChild(link)
  link.click()
  link.remove()
}

function mensagemStatusBatch(
  status: FinanceiroBatchStatusResponse | null,
  enviando: boolean,
  monitorando: boolean,
  textosFinanceiro: Pick<FinanceTexts, "uploadingBatch" | "pollingEveryTwoSeconds" | "ready">,
) {
  if (enviando) {
    return textosFinanceiro.uploadingBatch
  }

  if (monitorando) {
    return textosFinanceiro.pollingEveryTwoSeconds
  }

  if (status) {
    return formatarStatusLote(status.status)
  }

  return textosFinanceiro.ready
}

function resumoProgressoLote(
  status: FinanceiroBatchStatusResponse | null,
  enviando: boolean,
  textosFinanceiro: Pick<FinanceTexts, "waitingForBatchToStart" | "processed" | "duplicated" | "failed">,
) {
  if (enviando || !status) {
    return textosFinanceiro.waitingForBatchToStart
  }

  const processados = Math.max(0, Number(status.processed_count ?? status.processed ?? 0))
  const duplicados = Math.max(0, Number(status.duplicated_count ?? status.duplicated ?? 0))
  const falhas = Math.max(0, Number(status.failed_count ?? status.failed ?? 0))

  if (status.status === "completed") {
    return `${processados} ${textosFinanceiro.processed}, ${duplicados} ${textosFinanceiro.duplicated}, ${falhas} ${textosFinanceiro.failed}.`
  }

  if (status.status === "failed") {
    return `${processados} ${textosFinanceiro.processed}, ${duplicados} ${textosFinanceiro.duplicated}, ${falhas} ${textosFinanceiro.failed}.`
  }

  return `${processados} ${textosFinanceiro.processed}, ${duplicados} ${textosFinanceiro.duplicated}, ${falhas} ${textosFinanceiro.failed}.`
}

function resumoEvolucaoSalarial(
  evolucao: FinanceiroEvolucaoSalarialResponse | null | undefined,
  textosFinanceiro: Pick<FinanceTexts, "noPaychecksYet" | "salaryAnalysisPersists" | "demoFigures">,
) {
  if (
    evolucao == null ||
    evolucao.ano_inicial == null ||
    evolucao.ano_final == null ||
    evolucao.salario_base_inicial_referencia == null ||
    evolucao.salario_base_final_referencia == null
  ) {
    return textosFinanceiro.noPaychecksYet
  }

  return `No período analisado, seu salário-base passou de ${formatarMoeda(
    evolucao.salario_base_inicial_referencia,
  )} para ${formatarMoeda(evolucao.salario_base_final_referencia)}. A remuneração bruta total também variou por causa de adicionais, auxílios e outras vantagens.`
}

type SerieLinha = {
  key: string
  label: string
  color: string
  values: number[]
}

type ColunaDesconto = {
  key: string
  label: string
}

const COLUNAS_DESCONTOS: ColunaDesconto[] = [
  { key: "previdencia", label: "Pension" },
  { key: "irrf", label: "IRRF" },
  { key: "emprestimo", label: "Loans" },
  { key: "saude", label: "Health" },
  { key: "outros_descontos", label: "Other discounts" },
]

const SALARY_BASE_SERIE: SerieLinha = {
  key: "salario_base",
  label: "Salary base",
  color: "#14b8a6",
  values: [],
}

const BRUTO_SERIE: SerieLinha = {
  key: "bruto_total",
  label: "Gross total",
  color: "#60a5fa",
  values: [],
}

const LIQUIDO_SERIE: SerieLinha = {
  key: "liquido",
  label: "Net pay",
  color: "#f97316",
  values: [],
}

type LineChartProps = {
  title: string
  subtitle: string
  years: number[]
  series: SerieLinha[]
  ariaLabel: string
  texts: Pick<FinanceTexts, "annualAnalysis" | "noAnnualData">
}

function calcularPontoLinha(
  index: number,
  total: number,
  value: number,
  maxValue: number,
  width: number,
  height: number,
  padding: { top: number; right: number; bottom: number; left: number },
) {
  const plotWidth = width - padding.left - padding.right
  const plotHeight = height - padding.top - padding.bottom
  const x = total <= 1 ? padding.left + plotWidth / 2 : padding.left + (index / (total - 1)) * plotWidth
  const y =
    maxValue <= 0
      ? padding.top + plotHeight
      : padding.top + plotHeight - (Math.max(value, 0) / maxValue) * plotHeight

  return { x, y }
}

function criarCaminhoSerie(
  values: number[],
  maxValue: number,
  width: number,
  height: number,
  padding: { top: number; right: number; bottom: number; left: number },
) {
  return values
    .map((value, index) => {
      const ponto = calcularPontoLinha(index, values.length, value, maxValue, width, height, padding)
      return `${index === 0 ? "M" : "L"} ${ponto.x} ${ponto.y}`
    })
    .join(" ")
}

function formatarEixoMoeda(valor: number) {
  return formatarMoeda(valor)
}

function LineChart({ title, subtitle, years, series, ariaLabel, texts }: LineChartProps) {
  const width = 960
  const height = 320
  const padding = { top: 24, right: 24, bottom: 56, left: 88 }
  const yearsSeguros = listaSegura(years)
  const seriesSeguras = listaSegura(series)
  const valores = seriesSeguras.flatMap((serie) => listaSegura(serie.values))
  const maxValue = Math.max(0, ...valores)
  const gridLines = 4
  const semDados = yearsSeguros.length === 0 || seriesSeguras.length === 0 || valores.length === 0

  return (
    <section className="chart-panel">
      <div className="analysis-header__title analysis-header__title--compact">
        <p className="eyebrow eyebrow--title">{texts.annualAnalysis}</p>
        <h3>{title}</h3>
        <p className="analysis-header__subtitle">{subtitle}</p>
      </div>

      {semDados ? (
        <div className="chart-empty">
          <p className="helper">{texts.noAnnualData}</p>
        </div>
      ) : (
        <div className="chart-canvas" aria-label={ariaLabel}>
          <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel}>
            <defs>
              <linearGradient id={`grid-${ariaLabel.replace(/\s+/g, "-").toLowerCase()}`} x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="rgba(148, 163, 184, 0.28)" />
                <stop offset="100%" stopColor="rgba(148, 163, 184, 0.08)" />
              </linearGradient>
            </defs>

            {Array.from({ length: gridLines + 1 }, (_, index) => {
              const y = padding.top + ((height - padding.top - padding.bottom) / gridLines) * index
              const value = maxValue - (maxValue / gridLines) * index
              return (
                <g key={`grid-${index}`}>
                  <line
                    className="chart-grid-line"
                    x1={padding.left}
                    x2={width - padding.right}
                    y1={y}
                    y2={y}
                  />
                  <text className="chart-axis-label chart-axis-label--y" x={padding.left - 12} y={y + 4}>
                    {formatarEixoMoeda(value)}
                  </text>
                </g>
              )
            })}

            {yearsSeguros.map((ano, index) => {
              const ponto = calcularPontoLinha(index, yearsSeguros.length, 0, 0, width, height, padding)
              return (
                <g key={`year-${ano}`}>
                  <line
                    className="chart-axis-tick"
                    x1={ponto.x}
                    x2={ponto.x}
                    y1={height - padding.bottom}
                    y2={height - padding.bottom + 8}
                  />
                  <text
                    className="chart-axis-label chart-axis-label--x"
                    x={ponto.x}
                    y={height - padding.bottom + 26}
                  >
                    {ano}
                  </text>
                </g>
              )
            })}

            <line
              className="chart-axis-baseline"
              x1={padding.left}
              x2={width - padding.right}
              y1={height - padding.bottom}
              y2={height - padding.bottom}
            />

            {seriesSeguras.map((serie) => {
              const valoresSerie = listaSegura(serie.values)
              const caminho = criarCaminhoSerie(valoresSerie, maxValue, width, height, padding)
              return (
                <g key={serie.key}>
                  <path
                    d={caminho}
                    fill="none"
                    stroke={serie.color}
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  {valoresSerie.map((value, index) => {
                    const ponto = calcularPontoLinha(
                      index,
                      valoresSerie.length,
                      value,
                      maxValue,
                      width,
                      height,
                      padding,
                    )

                    return (
                      <circle
                        key={`${serie.key}-${index}`}
                        cx={ponto.x}
                        cy={ponto.y}
                        r="4.5"
                        fill={serie.color}
                        stroke="rgba(8, 16, 30, 0.9)"
                        strokeWidth="2.5"
                      >
                        <title>
                          {`${serie.label} - ${yearsSeguros[index]}: ${formatarMoeda(value)}`}
                        </title>
                      </circle>
                    )
                  })}
                </g>
              )
            })}
          </svg>
        </div>
      )}

      <div className="chart-legend" aria-label={`${title} legend`}>
        {seriesSeguras.map((serie) => (
          <span className="chart-legend__item" key={serie.key}>
            <span className="chart-legend__swatch" style={{ background: serie.color }} />
            {serie.label}
          </span>
        ))}
      </div>
    </section>
  )
}

function obterValorDesconto(
  composicao: Record<string, number> | null | undefined,
  chave: string,
): number {
  return mapaNumericoSegura(composicao)[chave] ?? 0
}

export function FinanceiroView({ modoDemo }: FinanceiroViewProps) {
  const { language, texts } = useLanguage()
  const t = texts.finance
  const [arquivosSelecionados, setArquivosSelecionados] = useState<File[]>([])
  const [batchStatus, setBatchStatus] = useState<FinanceiroBatchStatusResponse | null>(null)
  const [evolucaoSalarial, setEvolucaoSalarial] = useState<FinanceiroEvolucaoSalarialResponse | null>(
    () => (modoDemo ? DEMO_FINANCEIRO_EVOLUCAO : null),
  )
  const [contrachequesSalvos, setContrachequesSalvos] = useState<FinanceiroContrachequeResumo[]>(
    () => (modoDemo ? DEMO_FINANCEIRO_CONTRACHEQUES : []),
  )
  const [batchId, setBatchId] = useState<number | null>(null)
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [erroEvolucao, setErroEvolucao] = useState<string | null>(null)
  const [erroImportacaoAutomatica, setErroImportacaoAutomatica] = useState<string | null>(null)
  const [criandoImportacaoAutomatica, setCriandoImportacaoAutomatica] = useState(false)
  const [importacaoTemporaria, setImportacaoTemporaria] =
    useState<FinanceiroImportacaoTemporariaCriacaoResponse | null>(null)
  const [mensagemImportacaoAutomatica, setMensagemImportacaoAutomatica] = useState<string | null>(null)
  const [mostrarTokenTemporario, setMostrarTokenTemporario] = useState(false)
  const [opcoesAvancadasAbertas, setOpcoesAvancadasAbertas] = useState(false)
  const [carregandoAnalisePersistida, setCarregandoAnalisePersistida] = useState(!modoDemo)

  const carregarAnalisePersistida = useCallback(async () => {
    if (modoDemo) {
      setEvolucaoSalarial(DEMO_FINANCEIRO_EVOLUCAO)
      setContrachequesSalvos(DEMO_FINANCEIRO_CONTRACHEQUES)
      setErroEvolucao(null)
      setCarregandoAnalisePersistida(false)
      return
    }

    setCarregandoAnalisePersistida(true)
    setErroEvolucao(null)

    try {
      const [evolucaoResultado, contrachequesResultado] = await Promise.allSettled([
        obterEvolucaoSalarialPersistida(),
        obterContrachequesSalvos(),
      ])

      if (evolucaoResultado.status === "fulfilled") {
        setEvolucaoSalarial(evolucaoResultado.value)
      } else {
        setEvolucaoSalarial(null)
        if (!(evolucaoResultado.reason instanceof ApiResponseError && evolucaoResultado.reason.status === 404)) {
          setErroEvolucao(
            formatarErroFinanceiro(evolucaoResultado.reason, language, "analise"),
          )
        }
      }

      if (contrachequesResultado.status === "fulfilled") {
        setContrachequesSalvos(listaSegura(contrachequesResultado.value))
      } else {
        setContrachequesSalvos([])
      }
    } catch (error) {
      setEvolucaoSalarial(null)
      setContrachequesSalvos([])
      setErroEvolucao(formatarErroFinanceiro(error, language, "analise"))
    } finally {
      setCarregandoAnalisePersistida(false)
    }
  }, [modoDemo, language])

  function selecionarArquivos(evento: ChangeEvent<HTMLInputElement>) {
    const selecionados = Array.from(evento.target.files ?? [])

    if (
      selecionados.some(
        (arquivo) =>
          arquivo.type !== "application/pdf" && !arquivo.name.toLowerCase().endsWith(".pdf"),
      )
    ) {
      setArquivosSelecionados([])
      setBatchStatus(null)
      setBatchId(null)
      setErro(language === "en" ? "Please select PDF files only." : "Selecione apenas arquivos PDF.")
      setErroEvolucao(null)
      return
    }

    setArquivosSelecionados(selecionados)
    setBatchStatus(null)
    setBatchId(null)
    setErro(null)
    setErroEvolucao(null)
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    if (modoDemo) {
      setErro(language === "en" ? "Demo mode uses sample data and does not accept uploads." : "O modo demo usa dados de exemplo e não aceita envios.")
      return
    }

    if (arquivosSelecionados.length === 0) {
      setErro(language === "en" ? "Select at least one PDF before continuing." : "Selecione pelo menos um PDF antes de continuar.")
      return
    }

    setEnviando(true)
    setErro(null)
    setErroEvolucao(null)
    setBatchStatus(null)
    setBatchId(null)

    try {
      const payload = new FormData()
      for (const arquivo of arquivosSelecionados) {
        payload.append("arquivos", arquivo)
      }

      const resposta = await enviarLoteContracheques(payload)
      if (!Number.isFinite(resposta.batch_id) || resposta.batch_id <= 0) {
        throw new Error(
          language === "en"
            ? "We could not create a valid batch for the selected PDFs."
            : "Não foi possível criar um lote válido para os PDFs selecionados.",
        )
      }
      setBatchId(resposta.batch_id)
      setBatchStatus({
        total: arquivosSelecionados.length,
        processed_count: 0,
        duplicated_count: 0,
        failed_count: 0,
        processed: 0,
        duplicated: 0,
        failed: 0,
        status: resposta.status,
        last_error_message: null,
        failure_messages: [],
      })
    } catch (error) {
      setBatchStatus(null)
      setBatchId(null)
      setErro(formatarErroFinanceiro(error, language, "envio"))
    } finally {
      setEnviando(false)
    }
  }

  function abrirAssistenteImportacao(token: string) {
    const url = `gestaodecarreira://import?token=${encodeURIComponent(token)}`
    const link = document.createElement("a")
    link.href = url
    link.rel = "noopener"
    link.target = "_self"
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  async function instalarAssistenteImportacao() {
    if (modoDemo) {
      setErroImportacaoAutomatica(
        language === "en"
          ? "Demo mode does not download the assistant."
          : "O modo demo não baixa o assistente.",
      )
      return
    }

    setErroImportacaoAutomatica(null)
    setMensagemImportacaoAutomatica(null)
    iniciarDownloadAssistente()
  }

  async function importarMeusContrachequesAutomaticamente() {
    if (modoDemo) {
      setErroImportacaoAutomatica(
        language === "en"
          ? "Demo mode does not start the import assistant."
          : "O modo demo não inicia o assistente de importação.",
      )
      return
    }

    setCriandoImportacaoAutomatica(true)
    setErroImportacaoAutomatica(null)
    setMensagemImportacaoAutomatica(null)
    setImportacaoTemporaria(null)
    setMostrarTokenTemporario(false)
    setOpcoesAvancadasAbertas(false)

    try {
      const resposta = await criarImportacaoTemporariaFinanceiro()
      setImportacaoTemporaria(resposta)
      abrirAssistenteImportacao(resposta.token)
    } catch (error) {
      setImportacaoTemporaria(null)
      setErroImportacaoAutomatica(formatarErroFinanceiro(error, language, "importacao", t))
    } finally {
      setCriandoImportacaoAutomatica(false)
    }
  }

  async function gerarTokenTemporario() {
    if (modoDemo) {
      setErroImportacaoAutomatica(
        language === "en"
          ? "Demo mode does not start the import assistant."
          : "O modo demo não inicia o assistente de importação.",
      )
      return
    }

    setCriandoImportacaoAutomatica(true)
    setErroImportacaoAutomatica(null)
    setMensagemImportacaoAutomatica(null)
    setMostrarTokenTemporario(false)

    try {
      const resposta = importacaoTemporaria ?? (await criarImportacaoTemporariaFinanceiro())
      setImportacaoTemporaria(resposta)
      setMostrarTokenTemporario(true)
      setOpcoesAvancadasAbertas(true)
      setMensagemImportacaoAutomatica(t.temporaryTokenReady)
    } catch (error) {
      setImportacaoTemporaria(null)
      setErroImportacaoAutomatica(formatarErroFinanceiro(error, language, "importacao", t))
    } finally {
      setCriandoImportacaoAutomatica(false)
    }
  }

  useEffect(() => {
    queueMicrotask(() => {
      void carregarAnalisePersistida()
    })
  }, [carregarAnalisePersistida])

  useEffect(() => {
    if (batchId === null) {
      return
    }

    const controller = new AbortController()

    void acompanharLoteFinanceiro({
      batchId,
      fetchStatus: obterStatusLoteFinanceiro,
      delayMs: INTERVALO_POLLING_MS,
      signal: controller.signal,
      onUpdate: (statusAtual: FinanceiroBatchStatusResponse) => {
        setBatchStatus(statusAtual)
      },
    })
      .then((statusFinal) => {
        setBatchStatus(statusFinal)
      })
      .catch((error) => {
        if (error instanceof Error && error.name === "AbortError") {
          return
        }

        setErro(formatarErroFinanceiro(error, language, "lote"))
      })

    return () => {
      controller.abort()
    }
  }, [batchId, language])

  useEffect(() => {
    if (!batchStatus || !isBatchTerminalStatus(batchStatus.status)) {
      return
    }

    queueMicrotask(() => {
      void carregarAnalisePersistida()
    })
  }, [batchStatus, carregarAnalisePersistida])

  const progresso = calcularProgressoLote(batchStatus)
  const monitorando = Boolean(
    batchId !== null && batchStatus && !isBatchTerminalStatus(batchStatus.status) && !enviando,
  )
  const statusAtual = mensagemStatusBatch(batchStatus, enviando, monitorando, t)
  const totalSelecionadoBytes = arquivosSelecionados.reduce((total, arquivo) => total + arquivo.size, 0)
  const totalSelecionadoArquivos = arquivosSelecionados.length
  const barraIndeterminada = enviando && batchStatus === null
  const serieEvolucao = listaSegura(evolucaoSalarial?.series)
  const anosEvolucao = serieEvolucao.map((item) => item.ano)
  const serieSalarioBase = serieEvolucao.map((item) => item.salario_base_referencia_anual)
  const serieBruto = serieEvolucao.map((item) => item.bruto_total_referencia_anual)
  const serieLiquido = serieEvolucao.map((item) => item.liquido_referencia_anual)
  const anosSemCrescimento = listaSegura(evolucaoSalarial?.anos_sem_crescimento_relevante)
  const evolucaoSemDados = Boolean(evolucaoSalarial && serieEvolucao.length === 0)
  const totalContrachequesSalvos = listaSegura(contrachequesSalvos).length
  const mensagensErroLote = listaSegura(batchStatus?.failure_messages)
  const erroPrincipalLote = batchStatus?.last_error_message ?? null
  const possuiEvolucao = Boolean(evolucaoSalarial && serieEvolucao.length > 0)

  return (
    <section className="analysis-card card">
      <div className="analysis-header">
          <div className="analysis-header__title">
          <p className="eyebrow eyebrow--title">{t.title}</p>
          <h2>{t.payStubBatch}</h2>
            <p className="analysis-header__subtitle">{t.subtitle}</p>
          </div>
      </div>

      <div className="analysis-stack">
        <section className="card finance-auto-import-panel">
          <div className="finance-auto-import-panel__hero">
            <h3>{t.autoImportSectionTitle}</h3>
            <p className="finance-auto-import-panel__subtitle">{t.autoImportSectionSubtitle}</p>
          </div>

          <div className="finance-auto-import-panel__cta-stack">
            <button
              className="primary-button button--large finance-auto-import-panel__primary-action"
              type="button"
              onClick={() => void importarMeusContrachequesAutomaticamente()}
              disabled={modoDemo || criandoImportacaoAutomatica}
            >
              {criandoImportacaoAutomatica ? t.autoImporting : t.autoImportButton}
            </button>

            <button
              className="ghost-button ghost-button--text finance-auto-import-panel__secondary-action"
              type="button"
              onClick={() => void instalarAssistenteImportacao()}
              disabled={modoDemo}
            >
              {t.assistantDownloadButton}
            </button>

            <p className="finance-auto-import-panel__note">{t.autoImportFallbackHint}</p>
          </div>

          {mensagemImportacaoAutomatica ? (
            <p className="finance-auto-import-panel__toast" aria-live="polite">
              {mensagemImportacaoAutomatica}
            </p>
          ) : null}

          {erroImportacaoAutomatica ? <p className="error-box">{erroImportacaoAutomatica}</p> : null}

          <details
            className="finance-auto-import-panel__advanced"
            open={opcoesAvancadasAbertas}
            onToggle={(event) => {
              setOpcoesAvancadasAbertas(event.currentTarget.open)
            }}
          >
            <summary>{t.advancedModeLabel}</summary>
            <p className="helper finance-auto-import-panel__advanced-hint">{t.advancedModeHint}</p>
            <div className="finance-auto-import-panel__advanced-actions">
              <button
                className="ghost-button"
                type="button"
                onClick={() => void gerarTokenTemporario()}
                disabled={criandoImportacaoAutomatica}
              >
                {t.generateTemporaryTokenButton}
              </button>
            </div>

            {mostrarTokenTemporario && importacaoTemporaria ? (
              <div className="finance-auto-import-panel__token-card">
                <p className="finance-auto-import-panel__token-label">{t.manualTokenTitle}</p>
                <code>{importacaoTemporaria.token}</code>
                <div className="finance-auto-import-panel__token-actions">
                  <button
                    className="ghost-button"
                    type="button"
                    onClick={() => {
                      if (!importacaoTemporaria) {
                        return
                      }

                      void (async () => {
                        try {
                          const copiou = await copiarTextoParaClipboard(importacaoTemporaria.token)
                          if (copiou) {
                            setMensagemImportacaoAutomatica(t.copiedToast)
                          }
                        } catch {
                          // Keep the fallback flow open even if clipboard access is blocked.
                        }
                      })()
                    }}
                    disabled={!importacaoTemporaria}
                  >
                    {t.copyTokenButton}
                  </button>
                </div>
                <p className="finance-auto-import-panel__token-hint">{t.manualTokenHint}</p>
              </div>
            ) : null}
          </details>
        </section>

        <form className="upload-shell" onSubmit={enviarFormulario}>
          <div className="upload-shell__header">
            <div>
              <p className="eyebrow">{t.batchTitle}</p>
              <h3>{t.uploadPdfs}</h3>
            </div>
            <span className="status-pill">{modoDemo ? t.demoDataOnly : statusAtual}</span>
          </div>

          <div className="upload-shell__collapsed">
            <label className="field">
              <span>{t.pdfFiles}</span>
              <input
                accept=".pdf,application/pdf"
                multiple
                type="file"
                disabled={modoDemo}
                onChange={selecionarArquivos}
              />
            </label>

            <p className="helper">{t.selectOneOrMorePdfs}</p>
            {modoDemo ? (
              <p className="helper">{t.demoReadOnly}</p>
            ) : null}
            <p className="helper">{t.largeBatchesCanTakeAWhile}</p>

            <div className="metric-strip metric-strip--selection">
              <div className="metric-line">
                <span>{t.selectedPdfs}</span>
                <strong>{totalSelecionadoArquivos}</strong>
              </div>
              <div className="metric-line">
                <span>{t.totalSize}</span>
                <strong>{formatarTamanhoArquivo(totalSelecionadoBytes)}</strong>
              </div>
            </div>

            {totalSelecionadoArquivos > 0 ? (
              <details className="batch-details">
                <summary>{`${t.viewDetails} (${totalSelecionadoArquivos})`}</summary>
                <div className="batch-details__content">
                  <p className="helper">{t.fileNamesStayCollapsed}</p>
                  <ul className="batch-details__list">
                    {arquivosSelecionados.slice(0, 12).map((arquivo) => (
                      <li key={`${arquivo.name}-${arquivo.size}`}>
                        <strong>{arquivo.name}</strong>
                        <span>{formatarTamanhoArquivo(arquivo.size)}</span>
                      </li>
                    ))}
                  </ul>
                  {totalSelecionadoArquivos > 12 ? (
                    <p className="helper">
                      {`+${totalSelecionadoArquivos - 12} ${t.additionalFilesHidden}`}
                    </p>
                  ) : null}
                </div>
              </details>
            ) : null}

            <div className="progress-list">
              <div className="progress-row">
                <div className="progress-row-header">
                  <span className="helper">{statusAtual}</span>
                  <strong>{barraIndeterminada ? "..." : `${progresso}%`}</strong>
                </div>
                <div
                  className={
                    barraIndeterminada
                      ? "progress-track progress-track--indeterminate"
                      : "progress-track"
                  }
                  aria-label={t.batchProcessingProgressLabel}
                  aria-busy={barraIndeterminada || monitorando}
                  role="progressbar"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={barraIndeterminada ? undefined : progresso}
                >
                  <div
                    className={
                      batchStatus?.status === "failed"
                        ? "progress-fill progress-fill--accent"
                        : "progress-fill"
                    }
                    style={{
                      width: barraIndeterminada ? "100%" : `${progresso}%`,
                    }}
                  />
                </div>
              </div>
            </div>

            <div className="actions-row">
              <button className="primary-button" type="submit" disabled={modoDemo || enviando || monitorando}>
                {modoDemo ? t.demoMode : enviando ? t.sendingBatch : t.analyzeBatch}
              </button>
            </div>

            {erro ? <p className="error-box">{erro}</p> : null}
          </div>
        </form>

        {batchStatus ? (
          <section className="summary-panel">
            <div className="analysis-header__title analysis-header__title--compact">
              <p className="eyebrow eyebrow--title">{t.batchMonitor}</p>
              <h3>{t.processingStatus}</h3>
              <p className="analysis-header__subtitle">{t.batchProgressSubtitle}</p>
            </div>

            <div className="metric-strip metric-strip--hero">
              <div className="metric-line">
                <span>{t.status}</span>
                <strong>{formatarStatusLote(batchStatus.status)}</strong>
              </div>
              <div className="metric-line">
                <span>{t.processed}</span>
                <strong>{batchStatus.processed_count ?? batchStatus.processed ?? 0}</strong>
              </div>
              <div className="metric-line">
                <span>{t.duplicated}</span>
                <strong>{batchStatus.duplicated_count ?? batchStatus.duplicated ?? 0}</strong>
              </div>
              <div className="metric-line">
                <span>{t.failed}</span>
                <strong>{batchStatus.failed_count ?? batchStatus.failed ?? 0}</strong>
              </div>
              <div className="metric-line">
                <span>{t.total}</span>
                <strong>{batchStatus.total}</strong>
              </div>
            </div>

            <div className="progress-list">
              <div className="progress-row">
                <div className="progress-row-header">
                  <span className="helper">{resumoProgressoLote(batchStatus, enviando, t)}</span>
                  <strong>{progresso}%</strong>
                </div>
                <div
                  className="progress-track"
                  aria-label="Batch completion progress"
                  role="progressbar"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={progresso}
                >
                  <div
                    className={
                      batchStatus.status === "failed" ? "progress-fill progress-fill--accent" : "progress-fill"
                    }
                    style={{ width: `${progresso}%` }}
                  />
                </div>
              </div>
            </div>

            {(batchStatus.duplicated_count ?? batchStatus.duplicated ?? 0) > 0 ? (
              <p className="helper">{t.somePaychecksAlreadyExisted}</p>
            ) : null}

            {(batchStatus.failed_count ?? batchStatus.failed ?? 0) > 0 ? (
              <p className="helper">{t.workerKeptGoingAfterFailures}</p>
            ) : null}

            {batchStatus && (batchStatus.failed_count ?? batchStatus.failed ?? 0) > 0 ? (
              <div className="error-box">
                <p className="error-box__title">
                  {erroPrincipalLote ? `${t.primaryIssue}: ${erroPrincipalLote}` : t.primaryIssueNotAvailable}
                </p>
                {mensagensErroLote.length > 0 ? (
                  <ul className="error-list">
                    {mensagensErroLote.map((mensagem, indice) => (
                      <li key={`${mensagem}-${indice}`}>{mensagem}</li>
                    ))}
                  </ul>
                ) : null}
              </div>
            ) : null}
          </section>
        ) : null}

        <section className="salary-panel">
          <div className="analysis-header__title analysis-header__title--compact">
            <p className="eyebrow eyebrow--title">{t.annualSalaryEvolution}</p>
            <h3>{t.savedSalaryAnalysis}</h3>
            <p className="analysis-header__subtitle">{t.salaryAnalysisPersists}</p>
            {modoDemo ? (
              <p className="helper">{t.demoFigures}</p>
            ) : null}
          </div>

          {carregandoAnalisePersistida ? (
            <p className="helper">{t.loadingSavedAnalysis}</p>
          ) : null}

          {!carregandoAnalisePersistida && (totalContrachequesSalvos === 0 || evolucaoSemDados) ? (
            <p className="helper">{t.noPaychecksYet}</p>
          ) : null}

          {erroEvolucao ? <p className="error-box">{erroEvolucao}</p> : null}

          {possuiEvolucao ? (
            <>
              <div className="metric-strip metric-strip--hero metric-strip--salary">
                <div className="metric-line">
                  <span>{t.analysisPeriod}</span>
                  <strong>{`${evolucaoSalarial?.ano_inicial ?? "-"} - ${evolucaoSalarial?.ano_final ?? "-"}`}</strong>
                </div>
                <div className="metric-line">
                  <span>{t.startingSalaryBase}</span>
                  <strong>{formatarMoeda(evolucaoSalarial?.salario_base_inicial_referencia ?? null)}</strong>
                </div>
                <div className="metric-line">
                  <span>{t.endingSalaryBase}</span>
                  <strong>{formatarMoeda(evolucaoSalarial?.salario_base_final_referencia ?? null)}</strong>
                </div>
                <div className="metric-line">
                  <span>{t.salaryBaseEvolution}</span>
                  <strong>
                    {formatarVariacaoPercentual(
                      evolucaoSalarial?.variacao_acumulada_salario_base_percentual ?? null,
                      language,
                    )}
                  </strong>
                </div>
              </div>

              <LineChart
                ariaLabel={language === "en" ? "Annual salary base evolution" : "Evolução anual da base salarial"}
                title={t.salaryBaseByYear}
                subtitle={t.salaryTrendExplainer}
                years={anosEvolucao}
                texts={{ annualAnalysis: t.annualAnalysis, noAnnualData: t.noAnnualData }}
                series={[
                  {
                    key: SALARY_BASE_SERIE.key,
                    label: SALARY_BASE_SERIE.label,
                    color: SALARY_BASE_SERIE.color,
                    values: serieSalarioBase,
                  },
                ]}
              />

              <LineChart
                ariaLabel="Annual gross and net pay evolution"
                title={t.grossTotalAndNetPay}
                subtitle={t.grossAndNetSubtitle}
                years={anosEvolucao}
                texts={{ annualAnalysis: t.annualAnalysis, noAnnualData: t.noAnnualData }}
                series={[
                  {
                    key: BRUTO_SERIE.key,
                    label: BRUTO_SERIE.label,
                    color: BRUTO_SERIE.color,
                    values: serieBruto,
                  },
                  {
                    key: LIQUIDO_SERIE.key,
                    label: LIQUIDO_SERIE.label,
                    color: LIQUIDO_SERIE.color,
                    values: serieLiquido,
                  },
                ]}
              />

              <section className="discounts-panel">
                <div className="analysis-header__title analysis-header__title--compact">
                  <p className="eyebrow eyebrow--title">{t.discounts}</p>
                  <h3>{t.annualSummaryTable}</h3>
                  <p className="analysis-header__subtitle">{t.summaryKeepsDeductionsReadable}</p>
                </div>

                <div className="table-wrap">
                  <table className="timeline-table timeline-table--compact">
                    <thead>
                      <tr>
                        <th>{t.year}</th>
                        <th>{t.pension}</th>
                        <th>{t.irrf}</th>
                        <th>{t.loans}</th>
                        <th>{t.health}</th>
                        <th>{t.otherDiscounts}</th>
                        <th>{t.totalLabel}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {serieEvolucao.map((item) => (
                        <tr key={item.ano}>
                          <td>
                            <strong>{item.ano}</strong>
                          </td>
                          {COLUNAS_DESCONTOS.map((coluna) => (
                            <td key={`${item.ano}-${coluna.key}`}>
                              {formatarMoeda(
                                obterValorDesconto(item.composicao_descontos_referencia_anual, coluna.key),
                              )}
                            </td>
                          ))}
                          <td>
                            <strong>{formatarMoeda(item.descontos_referencia_anual)}</strong>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>

              {anosSemCrescimento.length > 0 ? (
                <p className="helper">
                  {`${t.yearsWithoutRelevantGrowth}: ${anosSemCrescimento.join(", ")}.`}
                </p>
              ) : null}

              <p className="salary-summary">{resumoEvolucaoSalarial(evolucaoSalarial, t)}</p>
            </>
          ) : null}
        </section>
      </div>
    </section>
  )
}
