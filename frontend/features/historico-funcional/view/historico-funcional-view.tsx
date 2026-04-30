"use client"

import { useState } from "react"

import { useHistoricoFuncionalController } from "../controller/use-historico-funcional-controller"
import { formatarTipoEvento, type HistoricoFuncionalAnalise } from "../model/historico-funcional.model"

type HistoricoFuncionalViewProps = {
  usuarioId: number | null
  historicoInicial: HistoricoFuncionalAnalise | null
}

type StatusEvento = HistoricoFuncionalAnalise["eventos"][number]["status"]
type ResumoAfastamentos = NonNullable<HistoricoFuncionalAnalise["afastamentos_resumo"]>

const STATUS_ORDEM: StatusEvento[] = [
  "cumprindo",
  "estagio_probatorio",
  "atrasado",
  "nao_aplicavel",
]

const TIPOS_AFASTAMENTO = {
  aguardando_resultado_conclusivo_de_exame_pericial: "#f59e0b",
  licenca_para_tratamento_de_saude: "#5eead4",
} as const

function formatarData(valor: string | null) {
  if (!valor) {
    return "-"
  }

  return new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium" }).format(new Date(`${valor}T00:00:00`))
}

function formatarDuracaoEmAnos(dias: number) {
  const anos = Math.floor(dias / 365)
  const meses = Math.floor((dias % 365) / 30)
  return `${anos}a ${meses}m`
}

function formatarPorcentagem(valor: number) {
  return `${valor.toFixed(1).replace(".", ",")}%`
}

function statusLabel(status: StatusEvento) {
  if (status === "atrasado") {
    return "Atrasado"
  }

  if (status === "cumprindo") {
    return "Cumprindo"
  }

  if (status === "estagio_probatorio") {
    return "Em estágio probatório"
  }

  return "Não aplicável"
}

function corDoStatus(status: StatusEvento) {
  if (status === "atrasado") {
    return "#fb7185"
  }

  if (status === "estagio_probatorio") {
    return "#f59e0b"
  }

  if (status === "cumprindo") {
    return "#10b981"
  }

  return "#94a3b8"
}

function corTipoAfastamento(tipo: keyof typeof TIPOS_AFASTAMENTO) {
  return TIPOS_AFASTAMENTO[tipo]
}

function GraficoPizzaTempo({
  percentualTrabalhado,
  percentualRestante,
}: {
  percentualTrabalhado: number
  percentualRestante: number
}) {
  const percentualFormatado = Math.max(0, Math.min(percentualTrabalhado, 100))

  return (
    <div className="pie-visual">
      <div
        className="pie-visual__ring"
        style={{
          background: `conic-gradient(var(--accent) 0 ${percentualFormatado}%, rgba(148, 163, 184, 0.18) ${percentualFormatado}% 100%)`,
        }}
      >
        <div className="pie-visual__center">
          <strong>{formatarPorcentagem(percentualTrabalhado)}</strong>
          <span>trabalhado</span>
        </div>
      </div>
    </div>
  )
}

function GraficoPizzaAfastamentos({ resumo }: { resumo: ResumoAfastamentos }) {
  const total = Math.max(resumo.dias_totais, 1)
  const tipos = Object.entries(resumo.dias_por_tipo)
    .filter(([, dias]) => dias > 0)
    .sort((a, b) => b[1] - a[1]) as Array<[keyof typeof TIPOS_AFASTAMENTO, number]>

  let acumulado = 0
  const fatias = tipos.map(([tipo, dias]) => {
    const inicio = (acumulado / total) * 100
    acumulado += dias
    const fim = (acumulado / total) * 100
    return `${corTipoAfastamento(tipo)} ${inicio}% ${fim}%`
  })

  const background =
    fatias.length > 0
      ? `conic-gradient(${fatias.join(", ")})`
      : "conic-gradient(rgba(148, 163, 184, 0.18) 0 100%)"

  return (
    <div className="pie-visual pie-visual--afastamentos">
      <div className="pie-visual__ring" style={{ background }} />
    </div>
  )
}

function LinhaDoTempoGrafica({
  eventos,
  filtroStatus,
  onFiltroStatusChange,
}: {
  eventos: HistoricoFuncionalAnalise["eventos"]
  filtroStatus: StatusEvento | null
  onFiltroStatusChange: (status: StatusEvento | null) => void
}) {
  if (eventos.length === 0) {
    return (
      <div className="history-empty history-empty--compact">
        <p>O PDF não trouxe eventos suficientes para desenhar a linha do tempo.</p>
      </div>
    )
  }

  const eventosVisiveis = filtroStatus
    ? eventos.filter((evento) => evento.status === filtroStatus)
    : eventos
  const totalEventos = eventos.length
  const totalVisiveis = eventosVisiveis.length

  if (eventosVisiveis.length === 0) {
    return (
      <div className="history-empty history-empty--compact">
        <p>Não há eventos para esse filtro.</p>
        <button className="ghost-button ghost-button--compact" type="button" onClick={() => onFiltroStatusChange(null)}>
          Mostrar todos
        </button>
      </div>
    )
  }

  const ordenados = [...eventosVisiveis].sort(
    (a, b) => new Date(`${a.data_efetiva}T00:00:00`).getTime() - new Date(`${b.data_efetiva}T00:00:00`).getTime(),
  )
  const tempos = ordenados.map((evento) => new Date(`${evento.data_efetiva}T00:00:00`).getTime())
  const minimo = Math.min(...tempos)
  const maximo = Math.max(...tempos)
  const largura = 1000
  const altura = 280
  const margemX = 64
  const eixoY = 148
  const alcance = Math.max(maximo - minimo, 1)

  function posicaoX(indice: number) {
    if (ordenados.length === 1) {
      return largura / 2
    }

    const valor = tempos[indice]
    return margemX + ((valor - minimo) / alcance) * (largura - margemX * 2)
  }

  return (
    <div className="timeline-graph">
      <div className="timeline-graph__toolbar">
        <p className="helper">
          Clique em um status para filtrar a linha do tempo e ver só os eventos daquela faixa.
        </p>
        {filtroStatus ? (
          <button
            className="ghost-button ghost-button--compact"
            type="button"
            onClick={() => onFiltroStatusChange(null)}
          >
            Mostrar todos
          </button>
        ) : null}
      </div>
      {filtroStatus ? (
        <p className="helper">
          Mostrando {totalVisiveis} de {totalEventos} eventos.
        </p>
      ) : null}

      <svg
        aria-label="Linha do tempo dos eventos funcionais"
        className="timeline-graph__svg"
        preserveAspectRatio="none"
        viewBox={`0 0 ${largura} ${altura}`}
        role="img"
      >
        <line className="timeline-graph__axis" x1={margemX} x2={largura - margemX} y1={eixoY} y2={eixoY} />

        {ordenados.map((evento, indice) => {
          const x = posicaoX(indice)
          const y = indice % 2 === 0 ? 78 : 218
          const isAbove = y < eixoY
          const cor = corDoStatus(evento.status)

          return (
            <g key={`${evento.tipo}-${evento.data_efetiva}-${evento.descricao}`}>
              <line
                className="timeline-graph__spoke"
                x1={x}
                x2={x}
                y1={eixoY}
                y2={y}
                style={{ stroke: cor }}
              />
              <circle
                cx={x}
                cy={y}
                r="10"
                className="timeline-graph__node"
                style={{ fill: cor }}
              />
              <text
                className={`timeline-graph__label ${isAbove ? "timeline-graph__label--above" : "timeline-graph__label--below"}`}
                textAnchor="middle"
                x={x}
                y={isAbove ? y - 18 : y + 32}
              >
                {formatarTipoEvento(evento.tipo)}
              </text>
              <text
                className={`timeline-graph__label timeline-graph__label--muted ${isAbove ? "timeline-graph__label--above" : "timeline-graph__label--below"}`}
                textAnchor="middle"
                x={x}
                y={isAbove ? y + 8 : y + 52}
              >
                {formatarData(evento.data_efetiva)}
              </text>
            </g>
          )
        })}
      </svg>

      <div className="timeline-legend" role="group" aria-label="Filtrar eventos da linha do tempo">
        {STATUS_ORDEM.map((status) => {
          const total = eventos.filter((evento) => evento.status === status).length
          if (total === 0) {
            return null
          }

          const ativo = filtroStatus === status

          return (
            <button
              key={status}
              aria-pressed={ativo}
              className={
                ativo
                  ? "timeline-legend__chip timeline-legend__chip--active"
                  : "timeline-legend__chip"
              }
              type="button"
              onClick={() => onFiltroStatusChange(ativo ? null : status)}
            >
              <span
                aria-hidden="true"
                className="timeline-legend__chip-dot"
                style={{ background: corDoStatus(status) }}
              />
              <span>
                {statusLabel(status)} · {total}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export function HistoricoFuncionalView({
  usuarioId,
  historicoInicial,
}: HistoricoFuncionalViewProps) {
  const [filtroStatus, setFiltroStatus] = useState<StatusEvento | null>(null)
  const {
    arquivo,
    arquivoDownloadUrl,
    arquivoAfastamentos,
    anosCltAverbados,
    carregando,
    dataNascimento,
    erro,
    historico,
    modoAtualizacaoHistorico,
    modoAnexoAfastamentos,
    iniciarAnexoAfastamentos,
    iniciarAtualizacaoHistorico,
    recarregarHistorico,
    selecionarArquivo,
    selecionarArquivoAfastamentos,
    setAnosCltAverbados,
    setDataNascimento,
    usarCltMaximo,
    enviarFormulario,
  } = useHistoricoFuncionalController({
    usuarioId,
    historicoInicial,
  })

  const painel = historico ?? historicoInicial
  const resumo = painel?.resumo_grafico
  const resumoAfastamentos = painel?.afastamentos_resumo

  return (
    <section className="analysis-card card">
      <div className="analysis-header">
        <div className="analysis-header__title">
          <p className="eyebrow">Histórico funcional</p>
          <h2>Gestão de dados</h2>
          <p className="analysis-header__subtitle">Data management</p>
        </div>
        <span className="status-pill">{painel ? "salvo" : "aguardando PDF"}</span>
      </div>

      {painel && resumo ? (
        <section className="overview-panel">
          <div className="overview-panel__chart">
            <GraficoPizzaTempo
              percentualRestante={resumo.percentual_restante}
              percentualTrabalhado={resumo.percentual_trabalhado}
            />
            {resumoAfastamentos ? <GraficoPizzaAfastamentos resumo={resumoAfastamentos} /> : null}
          </div>

          <div className="overview-panel__content">
            <div className="metric-strip">
              <div className="metric-line">
                <span>Tempo trabalhado</span>
                <strong>{formatarDuracaoEmAnos(resumo.tempo_trabalhado_dias)}</strong>
              </div>
              <div className="metric-line">
                <span>Tempo restante</span>
                <strong>{formatarDuracaoEmAnos(resumo.tempo_restante_dias)}</strong>
              </div>
              <div className="metric-line">
                <span>Eventos</span>
                <strong>{resumo.eventos_totais}</strong>
              </div>
              {resumoAfastamentos ? (
                <div className="metric-line metric-line--danger">
                  <span>Dias afastados</span>
                  <strong>{resumoAfastamentos.dias_totais}</strong>
                </div>
              ) : null}
              <div className="metric-line">
                <span>Próxima progressão</span>
                <strong>{formatarData(painel.proxima_progressao_prevista)}</strong>
              </div>
            </div>

            <div className="status-stack">
              {STATUS_ORDEM.map((status) => {
                const total = resumo.eventos_por_status[status] ?? 0
                if (total === 0) {
                  return null
                }

                return (
                  <div key={status} className="status-stack__row">
                    <span>{statusLabel(status)}</span>
                    <strong>{total}</strong>
                  </div>
                )
              })}
            </div>

          </div>
        </section>
      ) : (
        <div className="history-empty">
          <p>
            Envie o PDF do histórico funcional para analisar os dados e montar os cálculos de carreira.
          </p>
          <p>
            Aqui você vai ver o tempo de trabalho, a previsão de aposentadoria e a próxima progressão e promoção.
          </p>
        </div>
      )}

      <section className="upload-shell">
        <div className="upload-shell__header">
          <div>
            <p className="eyebrow">Arquivos</p>
            <h3>{painel ? "Adicionar arquivos" : "Enviar documentos"}</h3>
          </div>

          <div className="upload-shell__actions">
            {painel ? (
              <button
                className="ghost-button ghost-button--compact"
                type="button"
                onClick={iniciarAnexoAfastamentos}
              >
                Anexar afastamentos
              </button>
            ) : null}
            {painel ? (
              <button
                className="ghost-button ghost-button--compact"
                type="button"
                onClick={iniciarAtualizacaoHistorico}
              >
                Atualizar histórico funcional
              </button>
            ) : null}
            {arquivoDownloadUrl ? (
              <a
                className="ghost-button ghost-button--compact"
                download={arquivo?.name ?? "historico-funcional.pdf"}
                href={arquivoDownloadUrl}
              >
                Baixar PDF
              </a>
            ) : null}
          </div>
        </div>

        {!painel || modoAtualizacaoHistorico ? (
          <form className="upload-form" onSubmit={enviarFormulario}>
            <label className="field">
              <span>PDF do histórico funcional</span>
              <input type="file" accept="application/pdf" onChange={selecionarArquivo} />
            </label>

            <div className="field-grid">
              <label className="field">
                <span>Data de nascimento</span>
                <input
                  type="date"
                  value={dataNascimento}
                  onChange={(evento) => setDataNascimento(evento.target.value)}
                  required
                />
              </label>

              <label className="field">
                <span>Anos de CLT averbados</span>
                <input
                  type="number"
                  min={0}
                  max={10}
                  value={anosCltAverbados}
                  onChange={(evento) => setAnosCltAverbados(Number(evento.target.value))}
                />
              </label>
            </div>

            <label className="field">
              <span>PDF dos afastamentos</span>
              <input type="file" accept="application/pdf" onChange={selecionarArquivoAfastamentos} />
            </label>

            {arquivoAfastamentos ? (
              <p className="helper">Arquivo de afastamentos selecionado: {arquivoAfastamentos.name}</p>
            ) : null}

            <div className="upload-actions">
              <button className="ghost-button" type="button" onClick={usarCltMaximo}>
                Preencher 10 anos de CLT
              </button>
            </div>

            <p className="helper">
              Você pode informar no máximo 10 anos de CLT. Se já tiver esse tempo, basta preencher `10` ou usar o atalho.
            </p>

            {arquivo ? <p className="helper">Arquivo selecionado: {arquivo.name}</p> : null}
            {usuarioId ? (
              <button className="ghost-button" type="button" onClick={() => void recarregarHistorico()}>
                Recarregar último salvo
              </button>
            ) : null}

            {erro ? <p className="error-box">{erro}</p> : null}
          </form>
        ) : painel && modoAnexoAfastamentos ? (
          <div className="upload-shell__collapsed upload-shell__collapsed--compact">
            <label className="field">
              <span>PDF dos afastamentos</span>
              <input type="file" accept="application/pdf" onChange={selecionarArquivoAfastamentos} />
            </label>

            {arquivoAfastamentos ? (
              <p className="helper">Arquivo de afastamentos selecionado: {arquivoAfastamentos.name}</p>
            ) : (
              <p className="helper">Selecione o PDF para anexar aos dados já salvos.</p>
            )}

            {erro ? <p className="error-box">{erro}</p> : null}
          </div>
        ) : (
          <div className="upload-shell__collapsed">
            <p className="helper">
              O último PDF já foi lido. Se quiser, você pode abrir essa área para enviar outro arquivo.
            </p>
            {erro ? <p className="error-box">{erro}</p> : null}
          </div>
        )}
      </section>

      {painel ? (
        <section className="timeline-panel">
          <div className="card-header card-header--tight">
            <div className="analysis-header__title">
              <p className="eyebrow">Linha do tempo</p>
              <h3>Leitura em gráfico</h3>
              <p className="analysis-header__subtitle">Status dos eventos ao longo da carreira</p>
            </div>
          </div>

          <div className="timeline-marcos">
            <article className="timeline-marco-card">
              <span>Próxima progressão</span>
              <strong>{formatarData(painel.proxima_progressao_prevista)}</strong>
              <p>Marco calculado a partir do fim do estágio probatório.</p>
            </article>
            <article className="timeline-marco-card">
              <span>Próxima promoção</span>
              <strong>{formatarData(painel.proxima_promocao_prevista)}</strong>
              <p>Usa a mesma base inicial da contagem de carreira.</p>
            </article>
          </div>

          <LinhaDoTempoGrafica
            eventos={painel.eventos}
            filtroStatus={filtroStatus}
            onFiltroStatusChange={setFiltroStatus}
          />
        </section>
      ) : null}
    </section>
  )
}


