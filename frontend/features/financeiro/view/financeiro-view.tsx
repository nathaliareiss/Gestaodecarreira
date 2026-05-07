"use client"

import { useEffect, useState, type ChangeEvent, type FormEvent } from "react"

import {
  acompanharLoteFinanceiro,
  calcularProgressoLote,
  formatarStatusLote,
  isBatchTerminalStatus,
} from "../model/financeiro-batch.mjs"
import {
  enviarLoteContracheques,
  obterStatusLoteFinanceiro,
} from "../model/financeiro.repository"
import type { FinanceiroBatchStatusResponse } from "../model/financeiro.model"

const INTERVALO_POLLING_MS = 2000

type ArquivoLoteExibido = {
  id: string
  nome: string
  tamanho: number
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

function statusArquivoBatch(status: FinanceiroBatchStatusResponse | null) {
  if (!status) {
    return "Queued"
  }

  if (status.status === "processing") {
    return "Processing"
  }

  if (status.status === "failed") {
    return "Failed"
  }

  return "Processed"
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

export function FinanceiroView() {
  const [arquivosSelecionados, setArquivosSelecionados] = useState<File[]>([])
  const [batchStatus, setBatchStatus] = useState<FinanceiroBatchStatusResponse | null>(null)
  const [batchId, setBatchId] = useState<number | null>(null)
  const [enviando, setEnviando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

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
      return
    }

    setArquivosSelecionados(selecionados)
    setBatchStatus(null)
    setBatchId(null)
    setErro(null)
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    if (arquivosSelecionados.length === 0) {
      setErro("Select at least one PDF before continuing.")
      return
    }

    setEnviando(true)
    setErro(null)
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

  const progresso = calcularProgressoLote(batchStatus)
  const monitorando = Boolean(
    batchId !== null && batchStatus && !isBatchTerminalStatus(batchStatus.status) && !enviando,
  )
  const statusAtual = mensagemStatusBatch(batchStatus, enviando, monitorando)
  const badgeArquivos = statusArquivoBatch(batchStatus)
  const arquivosExibidos: ArquivoLoteExibido[] = arquivosSelecionados.map((arquivo, indice) => ({
    id: `${arquivo.name}-${arquivo.lastModified}-${indice}`,
    nome: arquivo.name,
    tamanho: arquivo.size,
  }))

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

            {arquivosExibidos.length > 0 ? (
              <div className="progress-list">
                {arquivosExibidos.map((arquivo) => (
                  <div className="metric-card" key={arquivo.id}>
                    <div className="progress-row-header">
                      <div>
                        <strong>{arquivo.nome}</strong>
                        <p className="helper" style={{ margin: "0.3rem 0 0" }}>
                          {formatarTamanhoArquivo(arquivo.tamanho)}
                        </p>
                      </div>
                      <span className="timeline-badge timeline-badge--neutral">{badgeArquivos}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="helper">No PDF selected yet.</p>
            )}

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
                  "The cards below update automatically while the worker processes each uploaded PDF."
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
                  <span className="helper">Completion</span>
                  <strong>{progresso}%</strong>
                </div>
                <div className="progress-track" aria-label="Batch completion progress">
                  <div
                    className={
                      batchStatus.status === "failed" ? "progress-fill progress-fill--accent" : "progress-fill"
                    }
                    style={{ width: `${progresso}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="progress-list">
              {arquivosExibidos.map((arquivo) => (
                <div className="metric-card" key={`processed-${arquivo.id}`}>
                  <div className="progress-row-header">
                    <div>
                      <strong>{arquivo.nome}</strong>
                      <p className="helper" style={{ margin: "0.3rem 0 0" }}>
                        {formatarTamanhoArquivo(arquivo.tamanho)}
                      </p>
                    </div>
                    <span className="timeline-badge timeline-badge--success">
                      {isBatchTerminalStatus(batchStatus.status) ? "Processed" : "Processing"}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {batchStatus.failed > 0 ? (
              <p className="helper">
                The worker kept going after failures, so the batch can still finish with partial results.
              </p>
            ) : null}

            <details className="upload-shell__collapsed upload-shell__collapsed--compact">
              <summary className="helper">Raw batch JSON</summary>
              <pre
                className="helper"
                style={{
                  marginTop: "0.75rem",
                  whiteSpace: "pre-wrap",
                  overflowX: "auto",
                }}
              >
                {JSON.stringify(
                  {
                    batch_id: batchId,
                    ...batchStatus,
                    arquivos: arquivosExibidos.map((arquivo) => arquivo.nome),
                  },
                  null,
                  2,
                )}
              </pre>
            </details>
          </section>
        ) : null}
      </div>
    </section>
  )
}
