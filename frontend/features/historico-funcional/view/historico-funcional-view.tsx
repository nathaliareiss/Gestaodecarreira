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
type TooltipGrafico = {
  x: number
  y: number
  alinhamento: "above" | "below"
  titulo: string
  linhas: string[]
}

const CORES_AFASTAMENTO = {
  aguardando_resultado_conclusivo_de_exame_pericial: "#fb7185",
  licenca_para_tratamento_de_saude: "#5eead4",
} as const

const ROTULOS_AFASTAMENTO = {
  aguardando_resultado_conclusivo_de_exame_pericial: "Aguardando perícia",
  licenca_para_tratamento_de_saude: "Licença para tratamento de saúde",
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

function formatarAtraso(dataPrevista: string | null, dataEfetiva: string | null) {
  if (!dataPrevista || !dataEfetiva) {
    return null
  }

  const inicio = new Date(`${dataPrevista}T00:00:00`)
  const fim = new Date(`${dataEfetiva}T00:00:00`)
  const diferencaDias = Math.max(Math.floor((fim.getTime() - inicio.getTime()) / 86400000), 0)

  if (diferencaDias <= 0) {
    return null
  }

  const anos = Math.floor(diferencaDias / 365)
  const meses = Math.floor((diferencaDias % 365) / 30)
  const dias = diferencaDias % 30

  const partes: string[] = []
  if (anos > 0) {
    partes.push(`${anos} ano${anos > 1 ? "s" : ""}`)
  }
  if (meses > 0) {
    partes.push(`${meses} mes${meses > 1 ? "es" : ""}`)
  }
  if (partes.length === 0 && dias > 0) {
    partes.push(`${dias} dia${dias > 1 ? "s" : ""}`)
  }

  return partes.join(" e ")
}

function formatarPorcentagem(valor: number) {
  return `${valor.toFixed(1).replace(".", ",")}%`
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

function rotuloStatus(status: StatusEvento) {
  if (status === "atrasado") {
    return "Atrasado"
  }

  if (status === "estagio_probatorio") {
    return "Em estágio probatório"
  }

  if (status === "cumprindo") {
    return "Cumprindo"
  }

  return "Não aplicável"
}

function corTipoAfastamento(tipo: keyof typeof CORES_AFASTAMENTO) {
  return CORES_AFASTAMENTO[tipo]
}

function rotuloAfastamento(tipo: keyof typeof ROTULOS_AFASTAMENTO) {
  return ROTULOS_AFASTAMENTO[tipo]
}

function ExibirTooltip({ tooltip }: { tooltip: TooltipGrafico | null }) {
  if (!tooltip) {
    return null
  }

  return (
    <div
      className={`timeline-tooltip timeline-tooltip--${tooltip.alinhamento}`}
      style={{
        left: `${tooltip.x}%`,
        top: `${tooltip.y}%`,
      }}
    >
      <strong>{tooltip.titulo}</strong>
      {tooltip.linhas.map((linha) => (
        <span key={linha}>{linha}</span>
      ))}
    </div>
  )
}

function GraficoPizzaTempo({
  percentualTrabalhado,
}: {
  percentualTrabalhado: number
}) {
  const percentualFormatado = Math.max(0, Math.min(percentualTrabalhado, 100))

  return (
    <div className="pie-visual">
      <div
        className="pie-visual__ring"
        style={{
          background: `conic-gradient(var(--accent) 0 ${percentualFormatado}%, rgba(148, 163, 184, 0.18) ${percentualFormatado}% 100%)`,
          width: "240px",
          height: "240px",
          maxWidth: "100%",
          maxHeight: "100%",
        }}
      >
        <div className="pie-visual__center" style={{ overflow: "hidden" }}>
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
    .sort((a, b) => b[1] - a[1]) as Array<[keyof typeof CORES_AFASTAMENTO, number]>

  const fatias = tipos.reduce<Array<{ cor: string; inicio: number; fim: number }>>(
    (acumuladas, [tipo, dias]) => {
      const inicioAnterior = acumuladas.length > 0 ? acumuladas[acumuladas.length - 1].fim : 0
      const proporcao = (dias / total) * 100

      acumuladas.push({
        cor: corTipoAfastamento(tipo),
        inicio: inicioAnterior,
        fim: inicioAnterior + proporcao,
      })

      return acumuladas
    },
    [],
  )

  const background =
    fatias.length > 0
      ? `conic-gradient(${fatias.map((fatia) => `${fatia.cor} ${fatia.inicio}% ${fatia.fim}%`).join(", ")})`
      : "conic-gradient(rgba(148, 163, 184, 0.18) 0 100%)"

  return (
    <div className="pie-visual pie-visual--afastamentos">
      <div
        className="pie-visual__ring"
        style={{
          background,
          width: "240px",
          height: "240px",
          maxWidth: "100%",
          maxHeight: "100%",
        }}
      >
        <div className="pie-visual__center" style={{ overflow: "hidden" }}>
          <strong>{resumo.dias_totais}</strong>
          <span>afastado</span>
        </div>
      </div>
      <div className="pie-visual__legend">
        {tipos.map(([tipo, dias]) => (
          <div className="pie-visual__legend-item" key={tipo}>
            <span className="pie-visual__legend-dot" style={{ background: corTipoAfastamento(tipo) }} />
            <div>
              <strong>{rotuloAfastamento(tipo)}</strong>
              <span>{dias} dia(s)</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function LinhaDoTempoGrafica({ eventos }: { eventos: HistoricoFuncionalAnalise["eventos"] }) {
  const [tooltip, setTooltip] = useState<TooltipGrafico | null>(null)

  if (eventos.length === 0) {
    return (
      <div className="history-empty history-empty--compact">
        <p>O PDF não trouxe eventos suficientes para desenhar a linha do tempo.</p>
      </div>
    )
  }

  const ordenados = [...eventos].sort(
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

  function mostrarTooltip(evento: HistoricoFuncionalAnalise["eventos"][number], x: number, y: number, alinhamento: "above" | "below") {
    const atrasoFormatado = formatarAtraso(evento.data_prevista ?? null, evento.data_efetiva)
    setTooltip({
      x: (x / largura) * 100,
      y: (y / altura) * 100,
      alinhamento,
      titulo: formatarTipoEvento(evento.tipo),
      linhas: [
        `Data: ${formatarData(evento.data_efetiva)}`,
        `Status: ${
          evento.status === "atrasado" && atrasoFormatado
            ? `Atrasado - ${atrasoFormatado}`
            : rotuloStatus(evento.status)
        }`,
        evento.descricao,
      ],
    })
  }

  return (
    <div className="timeline-graph timeline-graph--interactive">
      <ExibirTooltip tooltip={tooltip} />
      <svg
        aria-label="Linha do tempo de progressões e promoções"
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
            <g
              key={`${evento.tipo}-${evento.data_efetiva}-${evento.descricao}`}
              onMouseEnter={() => mostrarTooltip(evento, x, y, isAbove ? "above" : "below")}
              onMouseLeave={() => setTooltip(null)}
            >
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
    </div>
  )
}

function GraficoComparativoTempo({
  painel,
}: {
  painel: HistoricoFuncionalAnalise
}) {
  const [tooltip, setTooltip] = useState<TooltipGrafico | null>(null)
  const afastamentos = painel.afastamentos || []

  if (afastamentos.length === 0) {
    return (
      <div className="career-bars">
        <div className="career-bars__title">
          <p className="eyebrow">Comparativo</p>
          <h3>Tempo trabalhado e afastamentos</h3>
        </div>
        <div className="history-empty history-empty--compact">
          <p>Você não possui afastamentos registrados para desenhar o comparativo.</p>
        </div>
      </div>
    )
  }

  const tempos = afastamentos.map(a => new Date(`${a.data_inicio}T00:00:00`).getTime())

  const inicioCarreira = new Date(`${painel.data_exercicio}T00:00:00`).getTime()
  const agora = new Date().getTime()

  const minimo = inicioCarreira
  const maximo = Math.max(agora, ...tempos)

  const largura = 1000
  const altura = 280
  const margemX = 104
  const eixoY = 148
  const alcance = Math.max(maximo - minimo, 1)

  function posicaoX(data: string) {
    const valor = new Date(`${data}T00:00:00`).getTime()
    const rawPos = margemX + ((valor - minimo) / alcance) * (largura - margemX * 2)
    return Math.max(margemX, Math.min(largura - margemX, rawPos))
  }

  const xHojeRaw = margemX + ((agora - minimo) / alcance) * (largura - margemX * 2)
  const xHoje = Math.max(margemX, Math.min(largura - margemX, xHojeRaw))

  const ordenados = [...afastamentos].sort((a, b) =>
    new Date(`${a.data_inicio}T00:00:00`).getTime() - new Date(`${b.data_inicio}T00:00:00`).getTime()
  )

  function mostrarTooltip(
    afastamento: HistoricoFuncionalAnalise["afastamentos"][number],
    x: number,
    y: number,
    alinhamento: "above" | "below",
  ) {
    setTooltip({
      x: (x / largura) * 100,
      y: (y / altura) * 100,
      alinhamento,
      titulo: rotuloAfastamento(afastamento.tipo),
      linhas: [
        `Início: ${formatarData(afastamento.data_inicio)}`,
        `Fim: ${formatarData(afastamento.data_fim)}`,
        `Mês/ano: ${afastamento.mes_ano_afastamento}`,
        `${afastamento.total_dias} dia(s)`,
        afastamento.dias_restantes_ate_pericia > 0
          ? `${afastamento.dias_restantes_ate_pericia} dia(s) até a perícia`
          : "Perícia concluída",
      ],
    })
  }

  return (
    <div className="career-bars">
      <div className="career-bars__title">
        <p className="eyebrow">Comparativo</p>
        <h3>Tempo trabalhado e afastamentos</h3>
      </div>

      <div className="timeline-graph timeline-graph--interactive">
        <ExibirTooltip tooltip={tooltip} />
        <svg
          aria-label="Linha do tempo de afastamentos e carreira"
          className="timeline-graph__svg"
          preserveAspectRatio="none"
          viewBox={`0 0 ${largura} ${altura}`}
          role="img"
        >
          {/* Linha: Tempo Trabalhado (Efetivo) */}
          <line className="timeline-graph__axis" x1={margemX} x2={xHoje} y1={eixoY} y2={eixoY} style={{ stroke: "var(--accent)", strokeWidth: 4 }} />

          <circle cx={xHoje} cy={eixoY} r="5" style={{ fill: "var(--accent)" }} />
          <text className="timeline-graph__label timeline-graph__label--muted" textAnchor="end" x={xHoje} y={eixoY + 22}>Hoje</text>

          <circle cx={margemX} cy={eixoY} r="4" style={{ fill: "var(--accent)" }} />
          <text className="timeline-graph__label timeline-graph__label--muted" textAnchor="end" x={margemX - 10} y={eixoY + 4}>Início</text>

          {ordenados.map((afastamento, indice) => {
            const x = posicaoX(afastamento.data_inicio)
            const y = indice % 2 === 0 ? 68 : 228
            const isAbove = y < eixoY
            const cor = corTipoAfastamento(afastamento.tipo)

            return (
              <g
                key={`${afastamento.tipo}-${afastamento.data_inicio}-${indice}`}
                onMouseEnter={() => mostrarTooltip(afastamento, x, y, isAbove ? "above" : "below")}
                onMouseLeave={() => setTooltip(null)}
              >
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
                  {afastamento.total_dias} dias
                </text>
                <text
                  className={`timeline-graph__label timeline-graph__label--muted ${isAbove ? "timeline-graph__label--above" : "timeline-graph__label--below"}`}
                  textAnchor="middle"
                  x={x}
                  y={isAbove ? y + 8 : y + 48}
                >
                  {formatarData(afastamento.data_inicio)}
                </text>
              </g>
            )
          })}
        </svg>
      </div>
    </div>
  )
}

function rotuloArmazenamento(origem: HistoricoFuncionalAnalise["armazenamento_origem"]) {
  return origem === "local" ? "storage local de fallback" : "Supabase Storage"
}

function rotuloProcessamento(origem: HistoricoFuncionalAnalise["processamento_origem"]) {
  return origem === "fila" ? "fila em segundo plano" : "processamento direto no backend"
}

export function HistoricoFuncionalView({
  usuarioId,
  historicoInicial,
}: HistoricoFuncionalViewProps) {
  const {
    arquivo,
    arquivoDownloadUrl,
    arquivoAfastamentos,
    anosCltAverbados,
    dataNascimento,
    erro,
    mensagemProcessamento,
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
  const afastamentoPericia = resumoAfastamentos?.dias_por_tipo.aguardando_resultado_conclusivo_de_exame_pericial ?? 0

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
              percentualTrabalhado={resumo.percentual_trabalhado}
            />
            {resumoAfastamentos ? <GraficoPizzaAfastamentos resumo={resumoAfastamentos} /> : null}
          </div>

          <div className="overview-panel__content">
            <p className="helper">
              Armazenamento do PDF: {rotuloArmazenamento(painel.armazenamento_origem)}.
            </p>
            <p className="helper">
              Processamento: {rotuloProcessamento(painel.processamento_origem)}.
            </p>
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
              {resumoAfastamentos ? (
                <div className="metric-line metric-line--danger">
                  <span>Aguardando perícia</span>
                  <strong>{afastamentoPericia}</strong>
                </div>
              ) : null}
              <div className="metric-line">
                <span>Próxima progressão</span>
                <strong>{formatarData(painel.proxima_progressao_prevista)}</strong>
              </div>
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

            {mensagemProcessamento ? <p className="helper">{mensagemProcessamento}</p> : null}
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

            {mensagemProcessamento ? <p className="helper">{mensagemProcessamento}</p> : null}
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

      {painel && resumo ? (
        <section className="timeline-panel">
          <div className="career-bars__title" style={{ marginBottom: "1.5rem" }}>
            <p className="eyebrow">Linha do tempo: progressões e promoções</p>
          </div>

          <LinhaDoTempoGrafica eventos={painel.eventos} />

          <GraficoComparativoTempo
            painel={painel}
          />
        </section>
      ) : null}
    </section>
  )
}




