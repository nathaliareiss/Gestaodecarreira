"use client"

import { useEffect, useState, type ChangeEvent, type FormEvent } from "react"

import {
  acompanharLoteFinanceiro,
  calcularProgressoLote,
  formatarStatusLote,
  isBatchTerminalStatus,
} from "../model/financeiro-batch.mjs"
import {
  obterEvolucaoSalarialLote,
  enviarLoteContracheques,
  obterStatusLoteFinanceiro,
} from "../model/financeiro.repository"
import type {
  FinanceiroBatchStatusResponse,
  FinanceiroEvolucaoSalarialResponse,
} from "../model/financeiro.model"

const INTERVALO_POLLING_MS = 2000

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

  const concluidos = status.processed + status.failed

  if (status.status === "completed") {
    return `Finished ${concluidos}/${status.total} PDFs.`
  }

  if (status.status === "failed") {
    return `${concluidos}/${status.total} PDFs handled, with ${status.failed} failed.`
  }

  return `${concluidos}/${status.total} PDFs processed so far.`
}

function resumoEvolucaoSalarial(evolucao: FinanceiroEvolucaoSalarialResponse) {
  if (
    evolucao.ano_inicial === null ||
    evolucao.ano_final === null ||
    evolucao.salario_base_inicial_referencia === null ||
    evolucao.salario_base_final_referencia === null
  ) {
    return "No valid pay stubs were processed in this batch, so there is no salary evolution to show."
  }

  return `No período analisado, seu salário-base passou de ${formatarMoeda(
    evolucao.salario_base_inicial_referencia,
  )} para ${formatarMoeda(evolucao.salario_base_final_referencia)}. A remuneração bruta total também variou por causa de adicionais, auxílios e outras vantagens.`
}

type ComposicaoLegendaItem = {
  key: string
  label: string
  color: string
  keys?: string[]
}

const COMPOSICAO_VANTAGENS: ComposicaoLegendaItem[] = [
  { key: "salario_base", label: "Salary base", color: "#14b8a6" },
  { key: "ade", label: "ADE", color: "#0f766e" },
  { key: "adicional_noturno", label: "Night bonus", color: "#06b6d4" },
  { key: "alimentacao", label: "Meals", color: "#3b82f6" },
  { key: "abono_vestimenta", label: "Wardrobe allowance", color: "#8b5cf6" },
  {
    key: "outros_vantagens",
    label: "Other benefits",
    color: "#64748b",
    keys: ["outros_vantagens", "decimo_terceiro", "ferias", "retroativo"],
  },
]

const COMPOSICAO_DESCONTOS: ComposicaoLegendaItem[] = [
  { key: "previdencia", label: "Pension", color: "#f97316" },
  { key: "irrf", label: "IRRF", color: "#ef4444" },
  { key: "emprestimo", label: "Loans", color: "#f59e0b" },
  { key: "saude", label: "Health", color: "#14b8a6" },
  {
    key: "outros_descontos",
    label: "Other discounts",
    color: "#64748b",
    keys: ["outros_descontos", "associacao"],
  },
]

function obterValorComposicao(
  composicao: Record<string, number>,
  item: ComposicaoLegendaItem,
): number {
  const chaves = item.keys ?? [item.key]
  return chaves.reduce((total, chave) => total + (composicao[chave] ?? 0), 0)
}

function totalComposicao(
  composicao: Record<string, number>,
  itens: ComposicaoLegendaItem[],
): number {
  return itens.reduce((total, item) => total + obterValorComposicao(composicao, item), 0)
}

export function FinanceiroView() {
  const [arquivosSelecionados, setArquivosSelecionados] = useState<File[]>([])
  const [batchStatus, setBatchStatus] = useState<FinanceiroBatchStatusResponse | null>(null)
  const [evolucaoSalarial, setEvolucaoSalarial] = useState<FinanceiroEvolucaoSalarialResponse | null>(null)
  const [batchId, setBatchId] = useState<number | null>(null)
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [erroEvolucao, setErroEvolucao] = useState<string | null>(null)

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
      setEvolucaoSalarial(null)
      setBatchId(null)
      setErro("Please select PDF files only.")
      setErroEvolucao(null)
      return
    }

    setArquivosSelecionados(selecionados)
    setBatchStatus(null)
    setEvolucaoSalarial(null)
    setBatchId(null)
    setErro(null)
    setErroEvolucao(null)
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    if (arquivosSelecionados.length === 0) {
      setErro("Select at least one PDF before continuing.")
      return
    }

    setEnviando(true)
    setErro(null)
    setErroEvolucao(null)
    setBatchStatus(null)
    setEvolucaoSalarial(null)
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
        processed: 0,
        failed: 0,
        status: resposta.status,
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
    if (batchId === null) {
      return
    }

    const controller = new AbortController()

    void acompanharLoteFinanceiro({
      batchId,
      fetchStatus: obterStatusLoteFinanceiro,
      delayMs: INTERVALO_POLLING_MS,
      signal: controller.signal,
      onUpdate: (statusAtual) => {
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
    if (
      batchId === null ||
      !batchStatus ||
      !isBatchTerminalStatus(batchStatus.status) ||
      batchStatus.processed === 0
    ) {
      return
    }

    let ativo = true

    void obterEvolucaoSalarialLote(batchId)
      .then((dados) => {
        if (!ativo) {
          return
        }

        setEvolucaoSalarial(dados)
      })
      .catch((error) => {
        if (!ativo) {
          return
        }

        setEvolucaoSalarial(null)
        setErroEvolucao(
          error instanceof Error
            ? error.message
            : "We could not load the salary evolution yet.",
        )
      })

    return () => {
      ativo = false
    }
  }, [batchId, batchStatus])

  const progresso = calcularProgressoLote(batchStatus)
  const monitorando = Boolean(
    batchId !== null && batchStatus && !isBatchTerminalStatus(batchStatus.status) && !enviando,
  )
  const statusAtual = mensagemStatusBatch(batchStatus, enviando, monitorando)
  const totalSelecionadoBytes = arquivosSelecionados.reduce((total, arquivo) => total + arquivo.size, 0)
  const totalSelecionadoArquivos = arquivosSelecionados.length
  const barraIndeterminada = enviando && batchStatus === null
  const serieEvolucao = evolucaoSalarial?.series ?? []
  const evolucaoSemDados = Boolean(evolucaoSalarial && evolucaoSalarial.series.length === 0)
  const maiorValorSerie = serieEvolucao.reduce(
    (maior, item) =>
      Math.max(maior, item.salario_base_referencia_anual),
    0,
  )
  const carregandoEvolucao = Boolean(
    batchId !== null &&
      batchStatus &&
      isBatchTerminalStatus(batchStatus.status) &&
      batchStatus.processed > 0 &&
      evolucaoSalarial === null &&
      erroEvolucao === null,
  )
  const loteSemContrachequesValidos = Boolean(
    batchStatus &&
      isBatchTerminalStatus(batchStatus.status) &&
      batchStatus.processed === 0,
  )
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
            <span className="status-pill">{statusAtual}</span>
          </div>

          <div className="upload-shell__collapsed">
            <label className="field">
              <span>PDF files</span>
              <input
                accept=".pdf,application/pdf"
                multiple
                type="file"
                onChange={selecionarArquivos}
              />
            </label>

            <p className="helper">
              Select one or more PDFs. The batch monitor will poll the backend every 2 seconds.
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
              <button className="primary-button" type="submit" disabled={enviando || monitorando}>
                {enviando ? "Sending batch..." : "Analyze batch"}
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
                <span>Batch Status</span>
                <strong>{formatarStatusLote(batchStatus.status)}</strong>
              </div>
              <div className="metric-line">
                <span>Processed</span>
                <strong>{batchStatus.processed}</strong>
              </div>
              <div className="metric-line">
                <span>Failed</span>
                <strong>{batchStatus.failed}</strong>
              </div>
              <div className="metric-line">
                <span>Total Files</span>
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

            {batchStatus.failed > 0 ? (
              <p className="helper">
                The worker kept going after failures, so the batch can still finish with partial results.
              </p>
            ) : null}

            {batchStatus && batchStatus.failed > 0 ? (
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

        {batchStatus && isBatchTerminalStatus(batchStatus.status) ? (
          <section className="salary-panel">
            <div className="analysis-header__title analysis-header__title--compact">
              <p className="eyebrow eyebrow--title">Annual Salary Evolution</p>
              <h3>{"Salary base and remuneration composition"}</h3>
              <p className="analysis-header__subtitle">
                {
                  "The analysis now separates salary base, additional benefits, and deductions to keep the contracheque composition clear."
                }
              </p>
            </div>

            {carregandoEvolucao ? <p className="helper">Calculating annual reference values...</p> : null}

            {loteSemContrachequesValidos ? (
              <p className="helper">
                No valid pay stubs were processed in this batch, so there is no salary evolution to show.
              </p>
            ) : null}

            {evolucaoSemDados ? (
              <p className="helper">
                No salary evolution data was generated for this batch, so there is no chart to display.
              </p>
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

                <div className="salary-base-chart" aria-label="Annual salary base chart">
                  {serieEvolucao.map((item) => {
                    const altura =
                      maiorValorSerie > 0
                        ? Math.max(12, (item.salario_base_referencia_anual / maiorValorSerie) * 100)
                        : 0

                    return (
                      <div className="salary-base-chart__year" key={item.ano}>
                        <div className="salary-base-chart__bar-track">
                          <div
                            className="salary-base-chart__bar-fill"
                            style={{ height: `${altura}%` }}
                          />
                        </div>
                        <strong>{item.ano}</strong>
                        <span>{formatarMoeda(item.salario_base_referencia_anual)}</span>
                        <small>{formatarVariacaoPercentual(item.variacao_percentual_salario_base_ano_a_ano)}</small>
                      </div>
                    )
                  })}
                </div>

                <div className="composition-grid">
                  <section className="composition-panel">
                    <div className="analysis-header__title analysis-header__title--compact">
                      <p className="eyebrow eyebrow--title">Remuneration composition</p>
                      <h3>{"Median reference by year"}</h3>
                      <p className="analysis-header__subtitle">
                        {
                          "Stacked bars show the salary base and the main additional benefits tracked in the contracheque."
                        }
                      </p>
                    </div>

                    <div className="salary-legend salary-legend--composition" aria-label="Remuneration composition legend">
                      {COMPOSICAO_VANTAGENS.map((item) => (
                        <span
                          className="salary-legend__item"
                          key={item.key}
                          style={{ borderColor: item.color, boxShadow: `inset 0 0 0 1px ${item.color}33` }}
                        >
                          <span
                            className="salary-legend__swatch"
                            style={{ background: item.color }}
                          />
                          {item.label}
                        </span>
                      ))}
                    </div>

                    <div className="composition-chart" aria-label="Remuneration composition chart">
                      {serieEvolucao.map((item) => {
                        const composicao = item.composicao_vantagens_referencia_anual
                        const total = totalComposicao(composicao, COMPOSICAO_VANTAGENS)

                        return (
                          <div className="composition-chart__year" key={item.ano}>
                            <div className="composition-chart__stack">
                              {COMPOSICAO_VANTAGENS.map((segmento) => {
                                const valor = obterValorComposicao(composicao, segmento)
                                const altura = total > 0 ? Math.max(4, (valor / total) * 100) : 0

                                return (
                                  <div
                                    className="composition-chart__segment"
                                    key={segmento.key}
                                    style={{ height: `${altura}%`, background: segmento.color }}
                                    title={`${segmento.label}: ${formatarMoeda(valor)}`}
                                  />
                                )
                              })}
                            </div>
                            <strong>{item.ano}</strong>
                            <span>{formatarMoeda(total)}</span>
                          </div>
                        )
                      })}
                    </div>
                  </section>

                  <section className="composition-panel">
                    <div className="analysis-header__title analysis-header__title--compact">
                      <p className="eyebrow eyebrow--title">Discounts</p>
                      <h3>{"Median reference by year"}</h3>
                      <p className="analysis-header__subtitle">
                        {
                          "Here we keep the discount block separate so pension, tax, loans, and health deductions stay easy to read."
                        }
                      </p>
                    </div>

                    <div className="salary-legend salary-legend--composition" aria-label="Discount legend">
                      {COMPOSICAO_DESCONTOS.map((item) => (
                        <span
                          className="salary-legend__item"
                          key={item.key}
                          style={{ borderColor: item.color, boxShadow: `inset 0 0 0 1px ${item.color}33` }}
                        >
                          <span
                            className="salary-legend__swatch"
                            style={{ background: item.color }}
                          />
                          {item.label}
                        </span>
                      ))}
                    </div>

                    <div className="composition-chart" aria-label="Discount composition chart">
                      {serieEvolucao.map((item) => {
                        const composicao = item.composicao_descontos_referencia_anual
                        const total = totalComposicao(composicao, COMPOSICAO_DESCONTOS)

                        return (
                          <div className="composition-chart__year" key={item.ano}>
                            <div className="composition-chart__stack">
                              {COMPOSICAO_DESCONTOS.map((segmento) => {
                                const valor = obterValorComposicao(composicao, segmento)
                                const altura = total > 0 ? Math.max(4, (valor / total) * 100) : 0

                                return (
                                  <div
                                    className="composition-chart__segment"
                                    key={segmento.key}
                                    style={{ height: `${altura}%`, background: segmento.color }}
                                    title={`${segmento.label}: ${formatarMoeda(valor)}`}
                                  />
                                )
                              })}
                            </div>
                            <strong>{item.ano}</strong>
                            <span>{formatarMoeda(total)}</span>
                          </div>
                        )
                      })}
                    </div>
                  </section>
                </div>

                {evolucaoSalarial.anos_sem_crescimento_relevante.length > 0 ? (
                  <p className="helper">
                    {`Years without relevant growth: ${evolucaoSalarial.anos_sem_crescimento_relevante.join(", ")}.`}
                  </p>
                ) : null}

                <p className="salary-summary">{resumoEvolucaoSalarial(evolucaoSalarial)}</p>
              </>
            ) : null}
          </section>
        ) : null}
      </div>
    </section>
  )
}

