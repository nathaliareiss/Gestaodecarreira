"use client"

import { useEffect, useState, type ChangeEvent, type FormEvent } from "react"

import {
  acompanharLoteFinanceiro,
  calcularProgressoLote,
  formatarStatusLote,
  isBatchTerminalStatus,
} from "../model/financeiro-batch.mjs"
import {
  obterContrachequesSalvos,
  obterEvolucaoSalarialPersistida,
  enviarLoteContracheques,
  obterStatusLoteFinanceiro,
} from "../model/financeiro.repository"
import type {
  FinanceiroContrachequeResumo,
  FinanceiroBatchStatusResponse,
  FinanceiroEvolucaoSalarialResponse,
} from "../model/financeiro.model"
import {
  DEMO_FINANCEIRO_CONTRACHEQUES,
  DEMO_FINANCEIRO_EVOLUCAO,
} from "@/shared/demo/demo-data"

const INTERVALO_POLLING_MS = 2000

type FinanceiroViewProps = {
  modoDemo: boolean
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
  if (valor === null || !Number.isFinite(valor)) {
    return "-"
  }

  return formatadorMoeda.format(valor)
}

function formatarVariacaoPercentual(valor: number | null) {
  if (valor === null || !Number.isFinite(valor)) {
    return "Base year"
  }

  const sinal = valor > 0 ? "+" : ""
  return `${sinal}${valor.toFixed(2)}%`
}

function mensagemStatusBatch(status: FinanceiroBatchStatusResponse | null, enviando: boolean, monitorando: boolean) {
  if (enviando) {
    return "Uploading batch..."
  }

  if (monitorando) {
    return "Polling every 2 seconds..."
  }

  if (status) {
    return formatarStatusLote(status.status)
  }

  return "Ready"
}

function resumoProgressoLote(status: FinanceiroBatchStatusResponse | null, enviando: boolean) {
  if (enviando || !status) {
    return "Waiting for the batch to start..."
  }

  const processados = Math.max(0, Number(status.processed_count ?? status.processed ?? 0))
  const duplicados = Math.max(0, Number(status.duplicated_count ?? status.duplicated ?? 0))
  const falhas = Math.max(0, Number(status.failed_count ?? status.failed ?? 0))

  if (status.status === "completed") {
    return `${processados} processados, ${duplicados} duplicados, ${falhas} falharam.`
  }

  if (status.status === "failed") {
    return `${processados} processados, ${duplicados} duplicados, ${falhas} falharam.`
  }

  return `${processados} processados, ${duplicados} duplicados, ${falhas} falharam.`
}

function resumoEvolucaoSalarial(evolucao: FinanceiroEvolucaoSalarialResponse) {
  if (
    evolucao.ano_inicial === null ||
    evolucao.ano_final === null ||
    evolucao.salario_base_inicial_referencia === null ||
    evolucao.salario_base_final_referencia === null
  ) {
    return "Você ainda não enviou contracheques."
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

function LineChart({ title, subtitle, years, series, ariaLabel }: LineChartProps) {
  const width = 960
  const height = 320
  const padding = { top: 24, right: 24, bottom: 56, left: 88 }
  const valores = series.flatMap((serie) => serie.values)
  const maxValue = Math.max(0, ...valores)
  const gridLines = 4

  return (
    <section className="chart-panel">
      <div className="analysis-header__title analysis-header__title--compact">
        <p className="eyebrow eyebrow--title">Annual analysis</p>
        <h3>{title}</h3>
        <p className="analysis-header__subtitle">{subtitle}</p>
      </div>

      {years.length === 0 ? (
        <div className="chart-empty">
          <p className="helper">No annual data is available yet.</p>
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

            {years.map((ano, index) => {
              const ponto = calcularPontoLinha(index, years.length, 0, 0, width, height, padding)
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

            {series.map((serie) => {
              const caminho = criarCaminhoSerie(serie.values, maxValue, width, height, padding)
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
                  {serie.values.map((value, index) => {
                    const ponto = calcularPontoLinha(
                      index,
                      serie.values.length,
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
                          {`${serie.label} - ${years[index]}: ${formatarMoeda(value)}`}
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
        {series.map((serie) => (
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
  composicao: Record<string, number>,
  chave: string,
): number {
  return composicao[chave] ?? 0
}

export function FinanceiroView({ modoDemo }: FinanceiroViewProps) {
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
  const [carregandoAnalisePersistida, setCarregandoAnalisePersistida] = useState(!modoDemo)

  async function carregarAnalisePersistida() {
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
      const evolucaoPersistida = await obterEvolucaoSalarialPersistida()
      const contrachequesPersistidos = await obterContrachequesSalvos().catch(() => [])

      setEvolucaoSalarial(evolucaoPersistida)
      setContrachequesSalvos(contrachequesPersistidos)
    } catch (error) {
      setEvolucaoSalarial(null)
      setContrachequesSalvos([])
      setErroEvolucao(
        error instanceof Error ? error.message : "We could not load the saved salary analysis.",
      )
    } finally {
      setCarregandoAnalisePersistida(false)
    }
  }

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
      setErro("Please select PDF files only.")
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
      setErro("Demo mode uses sample data and does not accept uploads.")
      return
    }

    if (arquivosSelecionados.length === 0) {
      setErro("Select at least one PDF before continuing.")
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
      setErro(
        error instanceof Error
          ? error.message
          : "We could not start the batch. Check the PDFs and try again.",
      )
    } finally {
      setEnviando(false)
    }
  }

  useEffect(() => {
    queueMicrotask(() => {
      void carregarAnalisePersistida()
    })
  }, [modoDemo])

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

        setErro(
          error instanceof Error
            ? error.message
            : "We could not monitor the batch. Please try again.",
        )
      })

    return () => {
      controller.abort()
    }
  }, [batchId])

  useEffect(() => {
    if (!batchStatus || !isBatchTerminalStatus(batchStatus.status)) {
      return
    }

    queueMicrotask(() => {
      void carregarAnalisePersistida()
    })
  }, [batchStatus])

  const progresso = calcularProgressoLote(batchStatus)
  const monitorando = Boolean(
    batchId !== null && batchStatus && !isBatchTerminalStatus(batchStatus.status) && !enviando,
  )
  const statusAtual = mensagemStatusBatch(batchStatus, enviando, monitorando)
  const totalSelecionadoBytes = arquivosSelecionados.reduce((total, arquivo) => total + arquivo.size, 0)
  const totalSelecionadoArquivos = arquivosSelecionados.length
  const barraIndeterminada = enviando && batchStatus === null
  const serieEvolucao = evolucaoSalarial?.series ?? []
  const anosEvolucao = serieEvolucao.map((item) => item.ano)
  const serieSalarioBase = serieEvolucao.map((item) => item.salario_base_referencia_anual)
  const serieBruto = serieEvolucao.map((item) => item.bruto_total_referencia_anual)
  const serieLiquido = serieEvolucao.map((item) => item.liquido_referencia_anual)
  const evolucaoSemDados = Boolean(evolucaoSalarial && evolucaoSalarial.series.length === 0)
  const totalContrachequesSalvos = contrachequesSalvos.length
  const mensagensErroLote = batchStatus?.failure_messages ?? []
  const erroPrincipalLote = batchStatus?.last_error_message ?? null

  return (
    <section className="analysis-card card">
      <div className="analysis-header">
        <div className="analysis-header__title">
          <p className="eyebrow eyebrow--title">Finance</p>
          <h2>{"Batch Financial Analysis"}</h2>
            <p className="analysis-header__subtitle">
              {
                "Upload one or more pay stubs, then follow the batch progress in real time until the worker finishes."
              }
            </p>
          </div>
      </div>

      <div className="analysis-stack">
        <form className="upload-shell" onSubmit={enviarFormulario}>
          <div className="upload-shell__header">
            <div>
              <p className="eyebrow">Pay Stub Batch</p>
              <h3>Upload PDFs</h3>
            </div>
            <span className="status-pill">{modoDemo ? "Demo data only" : statusAtual}</span>
          </div>

          <div className="upload-shell__collapsed">
            <label className="field">
              <span>PDF files</span>
              <input
                accept=".pdf,application/pdf"
                multiple
                type="file"
                disabled={modoDemo}
                onChange={selecionarArquivos}
              />
            </label>

            <p className="helper">
              Select one or more PDFs. The batch monitor will poll the backend every 2 seconds.
            </p>
            {modoDemo ? (
              <p className="helper">
                Demo mode keeps this section read-only because the financial analysis is already loaded.
              </p>
            ) : null}
            <p className="helper">
              Large batches can take a few minutes. The worker keeps processing in the background.
            </p>

            <div className="metric-strip metric-strip--selection">
              <div className="metric-line">
                <span>Selected PDFs</span>
                <strong>{totalSelecionadoArquivos}</strong>
              </div>
              <div className="metric-line">
                <span>Total size</span>
                <strong>{formatarTamanhoArquivo(totalSelecionadoBytes)}</strong>
              </div>
            </div>

            {totalSelecionadoArquivos > 0 ? (
              <details className="batch-details">
                <summary>Ver detalhes ({totalSelecionadoArquivos})</summary>
                <div className="batch-details__content">
                  <p className="helper">
                    File names stay collapsed so the page stays light even with large batches.
                  </p>
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
                      {`+${totalSelecionadoArquivos - 12} additional files are hidden from the preview.`}
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
                  aria-label="Batch processing progress"
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
                {modoDemo ? "Demo mode" : enviando ? "Sending batch..." : "Analyze batch"}
              </button>
            </div>

            {erro ? <p className="error-box">{erro}</p> : null}
          </div>
        </form>

        {batchStatus ? (
          <section className="summary-panel">
            <div className="analysis-header__title analysis-header__title--compact">
              <p className="eyebrow eyebrow--title">Batch Monitor</p>
              <h3>{"Processing status"}</h3>
              <p className="analysis-header__subtitle">
                {
                  "A compact progress bar updates automatically while the worker processes each uploaded PDF."
                }
              </p>
            </div>

            <div className="metric-strip metric-strip--hero">
              <div className="metric-line">
                <span>Status</span>
                <strong>{formatarStatusLote(batchStatus.status)}</strong>
              </div>
              <div className="metric-line">
                <span>Processados</span>
                <strong>{batchStatus.processed_count ?? batchStatus.processed ?? 0}</strong>
              </div>
              <div className="metric-line">
                <span>Duplicados</span>
                <strong>{batchStatus.duplicated_count ?? batchStatus.duplicated ?? 0}</strong>
              </div>
              <div className="metric-line">
                <span>Falharam</span>
                <strong>{batchStatus.failed_count ?? batchStatus.failed ?? 0}</strong>
              </div>
              <div className="metric-line">
                <span>Total</span>
                <strong>{batchStatus.total}</strong>
              </div>
            </div>

            <div className="progress-list">
              <div className="progress-row">
                <div className="progress-row-header">
                  <span className="helper">{resumoProgressoLote(batchStatus, enviando)}</span>
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
              <p className="helper">Alguns contracheques já existiam e foram ignorados.</p>
            ) : null}

            {(batchStatus.failed_count ?? batchStatus.failed ?? 0) > 0 ? (
              <p className="helper">
                The worker kept going after failures, so the batch can still finish with partial results.
              </p>
            ) : null}

            {batchStatus && (batchStatus.failed_count ?? batchStatus.failed ?? 0) > 0 ? (
              <div className="error-box">
                <p className="error-box__title">
                  {erroPrincipalLote ? `Primary issue: ${erroPrincipalLote}` : "Primary issue not available."}
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
            <p className="eyebrow eyebrow--title">Annual Salary Evolution</p>
            <h3>{"Saved salary analysis"}</h3>
            <p className="analysis-header__subtitle">
              {"This section always loads the saved contracheques from PostgreSQL, so the data survives refresh."}
            </p>
            {modoDemo ? (
              <p className="helper">
                Demo figures are estimated from the 2015 and 2026 pay stubs you shared, so you can explore the
                salary trend without uploading files.
              </p>
            ) : null}
          </div>

          {carregandoAnalisePersistida ? (
            <p className="helper">Loading saved analysis from the database...</p>
          ) : null}

          {!carregandoAnalisePersistida && (totalContrachequesSalvos === 0 || evolucaoSemDados) ? (
            <p className="helper">Você ainda não enviou contracheques.</p>
          ) : null}

          {erroEvolucao ? <p className="error-box">{erroEvolucao}</p> : null}

          {evolucaoSalarial && evolucaoSalarial.series.length > 0 ? (
            <>
              <div className="metric-strip metric-strip--hero metric-strip--salary">
                <div className="metric-line">
                  <span>Analysis period</span>
                  <strong>{`${evolucaoSalarial.ano_inicial} - ${evolucaoSalarial.ano_final}`}</strong>
                </div>
                <div className="metric-line">
                  <span>Starting salary base</span>
                  <strong>{formatarMoeda(evolucaoSalarial.salario_base_inicial_referencia)}</strong>
                </div>
                <div className="metric-line">
                  <span>Ending salary base</span>
                  <strong>{formatarMoeda(evolucaoSalarial.salario_base_final_referencia)}</strong>
                </div>
                <div className="metric-line">
                  <span>Salary base evolution</span>
                  <strong>{formatarVariacaoPercentual(evolucaoSalarial.variacao_acumulada_salario_base_percentual)}</strong>
                </div>
              </div>

              <LineChart
                ariaLabel="Annual salary base evolution"
                title="Salary base by year"
                subtitle="A single line keeps the base salary trend clear and easy to scan."
                years={anosEvolucao}
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
                title="Gross total and net pay"
                subtitle="The second line chart keeps gross and liquid values separated without stacking blocks."
                years={anosEvolucao}
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
                  <p className="eyebrow eyebrow--title">Discounts</p>
                  <h3>{"Annual summary table"}</h3>
                  <p className="analysis-header__subtitle">
                    {"The summary keeps deductions readable without adding another heavy chart."}
                  </p>
                </div>

                <div className="table-wrap">
                  <table className="timeline-table timeline-table--compact">
                    <thead>
                      <tr>
                        <th>Year</th>
                        <th>Pension</th>
                        <th>IRRF</th>
                        <th>Loans</th>
                        <th>Health</th>
                        <th>Other discounts</th>
                        <th>Total</th>
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

              {evolucaoSalarial.anos_sem_crescimento_relevante.length > 0 ? (
                <p className="helper">
                  {`Years without relevant growth: ${evolucaoSalarial.anos_sem_crescimento_relevante.join(", ")}.`}
                </p>
              ) : null}

              <p className="salary-summary">{resumoEvolucaoSalarial(evolucaoSalarial)}</p>
            </>
          ) : null}
        </section>
      </div>
    </section>
  )
}

