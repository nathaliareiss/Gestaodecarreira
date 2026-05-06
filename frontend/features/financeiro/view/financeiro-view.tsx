"use client"

import { useState, type ChangeEvent, type FormEvent } from "react"

import { analisarContracheque } from "../model/financeiro.repository"
import type { ContrachequeAnalise, ValorFinanceiro } from "../model/financeiro.model"

type LinhaFinanceira = {
  label: string
  value: ValorFinanceiro
}

function formatarValor(valor: ValorFinanceiro) {
  if (valor === null || valor === undefined || valor === "") {
    return "-"
  }

  const numero = typeof valor === "number" ? valor : Number(valor)
  if (!Number.isFinite(numero)) {
    return String(valor)
  }

  return new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numero)
}

export function FinanceiroView() {
  const [arquivo, setArquivo] = useState<File | null>(null)
  const [resultado, setResultado] = useState<ContrachequeAnalise | null>(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  function selecionarArquivo(evento: ChangeEvent<HTMLInputElement>) {
    const selecionado = evento.target.files?.[0] ?? null

    if (selecionado && selecionado.type !== "application/pdf" && !selecionado.name.toLowerCase().endsWith(".pdf")) {
      setArquivo(null)
      setResultado(null)
      setErro("Selecione um arquivo PDF.")
      return
    }

    setArquivo(selecionado)
    setErro(null)
    setResultado(null)
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    if (!arquivo) {
      setErro("Selecione um contracheque em PDF antes de continuar.")
      return
    }

    setCarregando(true)
    setErro(null)

    try {
      const payload = new FormData()
      payload.append("arquivo", arquivo)

      const dados = await analisarContracheque(payload)
      setResultado(dados)
    } catch (error) {
      setResultado(null)
      setErro(
        error instanceof Error
          ? error.message
          : "Nao foi possivel analisar o contracheque. Verifique o PDF e tente novamente.",
      )
    } finally {
      setCarregando(false)
    }
  }

  const campos: LinhaFinanceira[] = resultado
    ? [
        { label: "Competência", value: resultado.competencia },
        { label: "Salário bruto", value: resultado.bruto },
        { label: "Total de descontos", value: resultado.descontos },
        { label: "Salário líquido", value: resultado.liquido },
        { label: "Vencimento básico", value: resultado.vencimento_basico },
        { label: "Adicional desempenho", value: resultado.adicional_desempenho },
        { label: "Adicional noturno", value: resultado.adicional_noturno },
        { label: "IRRF", value: resultado.irrf },
        { label: "Previdência", value: resultado.previdencia },
      ]
    : []

  return (
    <section className="analysis-card card">
      <div className="analysis-header">
        <div className="analysis-header__title">
          <p className="eyebrow eyebrow--title">Financeiro</p>
          <h2>Análise financeira</h2>
          <p className="analysis-header__subtitle">
            Envie seus contracheques para acompanhar sua evolução salarial ao longo da carreira.
          </p>
        </div>
      </div>

      <div className="analysis-stack">
        <form className="upload-shell" onSubmit={enviarFormulario}>
          <div className="upload-shell__header">
            <div>
              <p className="eyebrow">Contracheque</p>
              <h3>Upload PDF</h3>
            </div>
            <span className="status-pill">Apenas teste</span>
          </div>

          <div className="upload-shell__collapsed">
            <label className="field">
              <span>Arquivo PDF</span>
              <input type="file" accept="application/pdf" onChange={selecionarArquivo} />
            </label>

            {arquivo ? <p className="helper">Arquivo selecionado: {arquivo.name}</p> : null}

            <div className="actions-row">
              <button className="primary-button" type="submit" disabled={carregando}>
                {carregando ? "Analisando..." : "Analisar contracheque"}
              </button>
            </div>

            {erro ? <p className="error-box">{erro}</p> : null}
          </div>
        </form>

        {resultado ? (
          <section className="summary-panel">
            <div className="analysis-header__title analysis-header__title--compact">
              <p className="eyebrow eyebrow--title">Resultado</p>
              <h3>Dados extraídos</h3>
            </div>

            <div className="metric-strip">
              {campos.map((campo) => (
                <div className="metric-line" key={campo.label}>
                  <span>{campo.label}</span>
                  <strong>{campo.label === "Competência" ? String(campo.value ?? "-") : formatarValor(campo.value)}</strong>
                </div>
              ))}
            </div>

            <details className="upload-shell__collapsed upload-shell__collapsed--compact">
              <summary className="helper">JSON bruto</summary>
              <pre
                className="helper"
                style={{
                  marginTop: "0.75rem",
                  whiteSpace: "pre-wrap",
                  overflowX: "auto",
                }}
              >
                {JSON.stringify(resultado, null, 2)}
              </pre>
            </details>
          </section>
        ) : null}
      </div>
    </section>
  )
}
