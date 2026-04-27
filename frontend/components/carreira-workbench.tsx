"use client"

import { FormEvent, useState } from "react"

type ResumoCarreiraResponse = {
  nome: string
  data_nascimento: string
  data_ingresso: string
  tem_tempo_clt_averbado: boolean
  data_25_anos_carreira: string
  idade_na_data_25_anos_carreira: number
  possui_idade_minima_na_data_25_anos_carreira: boolean
  data_idade_minima_aposentadoria: string
  data_prevista_aposentadoria: string
  grau_aos_45_anos: string
  nivel_aos_45_anos: number
  grau_na_aposentadoria: string
  nivel_na_aposentadoria: number
}

type FormState = {
  nome: string
  data_nascimento: string
  data_ingresso: string
  tem_tempo_clt_averbado: boolean
}

const estadoInicial: FormState = {
  nome: "Maria",
  data_nascimento: "1980-01-01",
  data_ingresso: "2010-01-01",
  tem_tempo_clt_averbado: true,
}

function formatarData(iso: string) {
  const [ano, mes, dia] = iso.split("-")
  return `${dia}/${mes}/${ano}`
}

function formatarBooleano(valor: boolean) {
  return valor ? "sim" : "nao"
}

export function CarreiraWorkbench() {
  const [form, setForm] = useState<FormState>(estadoInicial)
  const [resumo, setResumo] = useState<ResumoCarreiraResponse | null>(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setCarregando(true)
    setErro(null)

    try {
      const response = await fetch(`${apiBaseUrl}/api/carreira/resumo`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      })

      const dados = (await response.json()) as
        | ResumoCarreiraResponse
        | { detail?: string }

      if (!response.ok) {
        throw new Error(dados && "detail" in dados ? dados.detail ?? "Erro ao calcular" : "Erro ao calcular")
      }

      setResumo(dados as ResumoCarreiraResponse)
    } catch (error) {
      setResumo(null)
      setErro(error instanceof Error ? error.message : "Falha inesperada")
    } finally {
      setCarregando(false)
    }
  }

  function carregarExemplo() {
    setForm(estadoInicial)
    setErro(null)
    setResumo(null)
  }

  return (
    <div className="workbench">
      <form className="card form-card" onSubmit={enviarFormulario}>
        <div className="card-header">
          <div>
            <p className="eyebrow">Testar a API</p>
            <h2>Cadastro da servidora</h2>
          </div>
          <button className="ghost-button" type="button" onClick={carregarExemplo}>
            Usar exemplo
          </button>
        </div>

        <label className="field">
          <span>Nome</span>
          <input
            value={form.nome}
            onChange={(evento) =>
              setForm((atual) => ({ ...atual, nome: evento.target.value }))
            }
            placeholder="Maria"
            required
          />
        </label>

        <div className="field-grid">
          <label className="field">
            <span>Data de nascimento</span>
            <input
              type="date"
              value={form.data_nascimento}
              onChange={(evento) =>
                setForm((atual) => ({ ...atual, data_nascimento: evento.target.value }))
              }
              required
            />
          </label>

          <label className="field">
            <span>Data de ingresso</span>
            <input
              type="date"
              value={form.data_ingresso}
              onChange={(evento) =>
                setForm((atual) => ({ ...atual, data_ingresso: evento.target.value }))
              }
              required
            />
          </label>
        </div>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={form.tem_tempo_clt_averbado}
            onChange={(evento) =>
              setForm((atual) => ({
                ...atual,
                tem_tempo_clt_averbado: evento.target.checked,
              }))
            }
          />
          <span>Tem tempo CLT averbado</span>
        </label>

        <div className="actions">
          <button className="primary-button" type="submit" disabled={carregando}>
            {carregando ? "Calculando..." : "Calcular resumo"}
          </button>
          <p className="helper">
            Front: <code>{apiBaseUrl}</code>
          </p>
        </div>

        {erro ? <p className="error-box">{erro}</p> : null}
      </form>

      <section className="card results-card">
        <div className="card-header">
          <div>
            <p className="eyebrow">Resultado</p>
            <h2>Resumo funcional</h2>
          </div>
          <span className="status-pill">{resumo ? "recebido" : "aguardando"}</span>
        </div>

        {resumo ? (
          <div className="results-grid">
            <div className="result-block">
              <span className="label">Nome</span>
              <strong>{resumo.nome}</strong>
            </div>
            <div className="result-block">
              <span className="label">Nascimento</span>
              <strong>{formatarData(resumo.data_nascimento)}</strong>
            </div>
            <div className="result-block">
              <span className="label">Ingresso</span>
              <strong>{formatarData(resumo.data_ingresso)}</strong>
            </div>
            <div className="result-block">
              <span className="label">CLT averbado</span>
              <strong>{formatarBooleano(resumo.tem_tempo_clt_averbado)}</strong>
            </div>
            <div className="result-block">
              <span className="label">25 anos de carreira</span>
              <strong>{formatarData(resumo.data_25_anos_carreira)}</strong>
            </div>
            <div className="result-block">
              <span className="label">Idade nessa data</span>
              <strong>{resumo.idade_na_data_25_anos_carreira} anos</strong>
            </div>
            <div className="result-block">
              <span className="label">Idade minima</span>
              <strong>{formatarData(resumo.data_idade_minima_aposentadoria)}</strong>
            </div>
            <div className="result-block">
              <span className="label">Pode aposentar</span>
              <strong>{formatarBooleano(resumo.possui_idade_minima_na_data_25_anos_carreira)}</strong>
            </div>
            <div className="result-block">
              <span className="label">Aposentadoria provavel</span>
              <strong>{formatarData(resumo.data_prevista_aposentadoria)}</strong>
            </div>
            <div className="result-block">
              <span className="label">Grau aos 45</span>
              <strong>
                {resumo.grau_aos_45_anos} / Nivel {resumo.nivel_aos_45_anos}
              </strong>
            </div>
            <div className="result-block">
              <span className="label">Grau na aposentadoria</span>
              <strong>
                {resumo.grau_na_aposentadoria} / Nivel {resumo.nivel_na_aposentadoria}
              </strong>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <p>
              Preencha o formulario e clique em <strong>Calcular resumo</strong> para
              enviar os dados ao backend Python.
            </p>
            <p>
              A resposta volta em JSON e o front organiza os calculos em cartoes para
              visualizacao.
            </p>
          </div>
        )}
      </section>
    </div>
  )
}
