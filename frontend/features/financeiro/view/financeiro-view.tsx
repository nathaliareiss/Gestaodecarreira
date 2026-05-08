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

function formatarMoeda(valor: number) {
  return formatadorMoeda.format(valor)
}

function formatarVariacaoPercentual(valor: number | null) {
  if (valor === null || !Number.isFinite(valor)) {
    return "Ano base"
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
  const anosSemCrescimento =
    evolucao.anos_sem_crescimento_relevante.length > 0
      ? `Anos sem crescimento relevante: ${evolucao.anos_sem_crescimento_relevante.join(", ")}.`
      : "Não houve anos sem crescimento relevante."

  return (
    `Período analisado: de ${evolucao.ano_inicial} a ${evolucao.ano_final}. ` +
    `Salário bruto de referência inicial: ${formatarMoeda(evolucao.bruto_inicial_referencia)}. ` +
    `Salário bruto de referência final: ${formatarMoeda(evolucao.bruto_final_referencia)}. ` +
    `Evolução acumulada: ${formatarVariacaoPercentual(evolucao.variacao_acumulada_bruto_percentual)}. ` +
    `Taxa média anual estimada (CAGR): ${formatarVariacaoPercentual(evolucao.cagr_bruto_percentual)}. ` +
    anosSemCrescimento
  )
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
    if (batchId === null || !batchStatus || !isBatchTerminalStatus(batchStatus.status)) {
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
  const maiorValorSerie = serieEvolucao.reduce(
    (maior, item) =>
      Math.max(maior, item.bruto_referencia_anual, item.liquido_referencia_anual),
    0,
  )
  const totalContrachequesEvolucao = serieEvolucao.reduce(
    (total, item) => total + item.quantidade_contracheques,
    0,
  )
  const carregandoEvolucao = Boolean(
    batchId !== null &&
      batchStatus &&
      isBatchTerminalStatus(batchStatus.status) &&
      evolucaoSalarial === null &&
      erroEvolucao === null,
  )

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
          </section>
        ) : null}

        {batchStatus && isBatchTerminalStatus(batchStatus.status) ? (
          <section className="salary-panel">
            <div className="analysis-header__title analysis-header__title--compact">
              <p className="eyebrow eyebrow--title">Evolução Salarial Anual</p>
              <h3>{"Bruto e líquido por ano"}</h3>
              <p className="analysis-header__subtitle">
                {
                  "O gráfico usa a mediana anual dos contracheques processados para reduzir distorções de 13º, férias, retroativos e outros meses atípicos."
                }
              </p>
            </div>

            <div className="salary-legend" aria-label="Legenda da evolução salarial">
              <span className="salary-legend__item salary-legend__item--gross">Bruto</span>
              <span className="salary-legend__item salary-legend__item--liquid">Líquido</span>
            </div>

            {carregandoEvolucao ? <p className="helper">Calculando a evolução anual...</p> : null}

            {erroEvolucao ? <p className="error-box">{erroEvolucao}</p> : null}

            {evolucaoSalarial ? (
              <>
                <div className="metric-strip metric-strip--hero metric-strip--salary">
                  <div className="metric-line">
                    <span>Ano inicial</span>
                    <strong>{evolucaoSalarial.ano_inicial}</strong>
                  </div>
                  <div className="metric-line">
                    <span>Bruto inicial</span>
                    <strong>{formatarMoeda(evolucaoSalarial.bruto_inicial_referencia)}</strong>
                  </div>
                  <div className="metric-line">
                    <span>Ano final</span>
                    <strong>{evolucaoSalarial.ano_final}</strong>
                  </div>
                  <div className="metric-line">
                    <span>Bruto final</span>
                    <strong>{formatarMoeda(evolucaoSalarial.bruto_final_referencia)}</strong>
                  </div>
                </div>

                <div className="metric-strip metric-strip--salary">
                  <div className="metric-line">
                    <span>Líquido inicial</span>
                    <strong>{formatarMoeda(evolucaoSalarial.liquido_inicial_referencia)}</strong>
                  </div>
                  <div className="metric-line">
                    <span>Líquido final</span>
                    <strong>{formatarMoeda(evolucaoSalarial.liquido_final_referencia)}</strong>
                  </div>
                  <div className="metric-line">
                    <span>Evolução acumulada</span>
                    <strong>{formatarVariacaoPercentual(evolucaoSalarial.variacao_acumulada_bruto_percentual)}</strong>
                  </div>
                  <div className="metric-line">
                    <span>CAGR estimado</span>
                    <strong>{formatarVariacaoPercentual(evolucaoSalarial.cagr_bruto_percentual)}</strong>
                  </div>
                </div>

                <div className="salary-chart" aria-label="Gráfico da evolução salarial anual">
                  {serieEvolucao.map((item) => {
                    const altura =
                      maiorValorSerie > 0
                        ? Math.max(14, (item.bruto_referencia_anual / maiorValorSerie) * 100)
                        : 0
                    const alturaLiquida =
                      maiorValorSerie > 0
                        ? Math.max(14, (item.liquido_referencia_anual / maiorValorSerie) * 100)
                        : 0

                    return (
                      <div className="salary-chart__year" key={item.ano}>
                        <div className="salary-chart__year-bars">
                          <div className="salary-chart__bar-block">
                            <div className="salary-chart__bar-track salary-chart__bar-track--gross">
                              <div
                                className="salary-chart__bar-fill salary-chart__bar-fill--gross"
                                style={{ height: `${altura}%` }}
                              />
                            </div>
                            <span>Bruto</span>
                          </div>
                          <div className="salary-chart__bar-block">
                            <div className="salary-chart__bar-track salary-chart__bar-track--liquid">
                              <div
                                className="salary-chart__bar-fill salary-chart__bar-fill--liquid"
                                style={{ height: `${alturaLiquida}%` }}
                              />
                            </div>
                            <span>Líquido</span>
                          </div>
                        </div>
                        <strong>{item.ano}</strong>
                        <span>{formatarMoeda(item.bruto_referencia_anual)}</span>
                        <small>{formatarMoeda(item.liquido_referencia_anual)}</small>
                        <small>{formatarMoeda(item.descontos_referencia_anual)} de descontos</small>
                        <small>{item.quantidade_contracheques} PDFs</small>
                        <p className="salary-chart__variation">
                          {formatarVariacaoPercentual(item.variacao_percentual_bruto_ano_a_ano)}
                          {item.crescimento_relevante ? "" : " sem crescimento relevante"}
                        </p>
                      </div>
                    )
                  })}
                </div>

                <p className="salary-summary">
                  {resumoEvolucaoSalarial(evolucaoSalarial)}
                </p>

                <p className="helper">
                  {`O gráfico cobre ${totalContrachequesEvolucao} contracheques processados.`}
                </p>
              </>
            ) : null}
          </section>
        ) : null}
      </div>
    </section>
  )
}
