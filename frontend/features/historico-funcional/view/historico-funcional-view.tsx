"use client"


import { useState } from "react"
import { useHistoricoFuncionalController } from "../controller/use-historico-funcional-controller"
import { formatarTipoEvento, type HistoricoFuncionalAnalise } from "../model/historico-funcional.model"
import { useLanguage } from "@/shared/i18n/language-provider"

type HistoricoFuncionalViewProps = {
  usuarioId: number | null
  historicoInicial: HistoricoFuncionalAnalise | null
  modoDemo: boolean
  onCreateAccount?: () => void
  criandoConta?: boolean
}

type StatusEvento = HistoricoFuncionalAnalise["eventos"][number]["status"]
type ResumoAfastamentos = NonNullable<HistoricoFuncionalAnalise["afastamentos_resumo"]>
type ResumoFerias = NonNullable<HistoricoFuncionalAnalise["ferias_resumo"]>
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
  aguardando_resultado_conclusivo_de_exame_pericial: "Medical Review",
  licenca_para_tratamento_de_saude: "Medical Leave",
} as const

const CORES_FERIAS = {
  regular: "#38bdf8",
  premium: "#a78bfa",
} as const

function formatarData(valor: string | null, idioma: "pt-BR" | "en") {
  if (!valor) {
    return "-"
  }

  return new Intl.DateTimeFormat(idioma === "en" ? "en-US" : "pt-BR", { dateStyle: "medium" }).format(
    new Date(`${valor}T00:00:00`),
  )
}

function formatarDuracaoEmAnos(dias: number, idioma: "pt-BR" | "en") {
  const anos = Math.floor(dias / 365)
  const meses = Math.floor((dias % 365) / 30)
  return idioma === "en" ? `${anos}y ${meses}mo` : `${anos}a ${meses}m`
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

function rotuloStatus(status: StatusEvento, idioma: "pt-BR" | "en") {
  if (status === "atrasado") {
    return idioma === "en" ? "Delayed" : "Atrasado"
  }

  if (status === "estagio_probatorio") {
    return idioma === "en" ? "Probation" : "Probatório"
  }

  if (status === "cumprindo") {
    return idioma === "en" ? "On Track" : "Em dia"
  }

  return "N/A"
}

function corTipoAfastamento(tipo: keyof typeof CORES_AFASTAMENTO) {
  return CORES_AFASTAMENTO[tipo]
}

function rotuloAfastamento(tipo: keyof typeof ROTULOS_AFASTAMENTO, idioma: "pt-BR" | "en") {
  if (idioma === "en") {
    return ROTULOS_AFASTAMENTO[tipo]
  }

  return tipo === "aguardando_resultado_conclusivo_de_exame_pericial"
    ? "Revisão médica"
    : "Licença médica"
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
  idioma,
}: {
  percentualTrabalhado: number
  idioma: "pt-BR" | "en"
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
          <span>{idioma === "en" ? "worked" : "trabalhado"}</span>
        </div>
      </div>
    </div>
  )
}


function GraficoPizzaAfastamentos({
  resumo,
  idioma,
}: {
  resumo: ResumoAfastamentos
  idioma: "pt-BR" | "en"
}) {
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
              <strong>{rotuloAfastamento(tipo, idioma)}</strong>
              <span>{`${dias} ${idioma === "en" ? "day(s)" : "dia(s)"}`}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function LinhaDoTempoGrafica({
  eventos,
  idioma,
}: {
  eventos: HistoricoFuncionalAnalise["eventos"]
  idioma: "pt-BR" | "en"
}) {
  const [tooltip, setTooltip] = useState<TooltipGrafico | null>(null)

  if (eventos.length === 0) {
    return (
      <div className="history-empty history-empty--compact">
        <p>{idioma === "en" ? "The PDF did not bring enough events to draw the timeline." : "O PDF não trouxe eventos suficientes para desenhar a linha do tempo."}</p>
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
        titulo: formatarTipoEvento(evento.tipo, idioma),
      linhas: [
        `${idioma === "en" ? "Date" : "Data"}: ${formatarData(evento.data_efetiva, idioma)}`,
        `${idioma === "en" ? "Status" : "Status"}: ${
          evento.status === "atrasado" && atrasoFormatado
            ? `${idioma === "en" ? "Delayed" : "Atrasado"} - ${atrasoFormatado}`
            : rotuloStatus(evento.status, idioma)
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
                {formatarTipoEvento(evento.tipo, idioma)}
              </text>
              <text
                className={`timeline-graph__label timeline-graph__label--muted ${isAbove ? "timeline-graph__label--above" : "timeline-graph__label--below"}`}
                textAnchor="middle"
                x={x}
                y={isAbove ? y + 8 : y + 52}
              >
                {formatarData(evento.data_efetiva, idioma)}
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
  idioma,
}: {
  painel: HistoricoFuncionalAnalise
  idioma: "pt-BR" | "en"
}) {
  const [tooltip, setTooltip] = useState<TooltipGrafico | null>(null)
  const afastamentos = painel.afastamentos || []

  if (afastamentos.length === 0) {
    return (
      <div className="career-bars">
        <div className="career-bars__title">
          <p className="eyebrow">{idioma === "en" ? "Comparison" : "Comparação"}</p>
          <h3>{idioma === "en" ? "Time Worked and Leave" : "Tempo trabalhado e afastamento"}</h3>
        </div>
        <div className="history-empty history-empty--compact">
          <p>{idioma === "en" ? "You do not have any recorded leave periods to draw the comparison." : "Você não possui períodos de afastamento registrados para desenhar a comparação."}</p>
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
      titulo: rotuloAfastamento(afastamento.tipo, idioma),
      linhas: [
        `${idioma === "en" ? "Start" : "Início"}: ${formatarData(afastamento.data_inicio, idioma)}`,
        `${idioma === "en" ? "End" : "Fim"}: ${formatarData(afastamento.data_fim, idioma)}`,
        `${idioma === "en" ? "Month/Year" : "Mês/Ano"}: ${afastamento.mes_ano_afastamento}`,
        `${afastamento.total_dias} ${idioma === "en" ? "day(s)" : "dia(s)"}`,
        afastamento.dias_restantes_ate_pericia > 0
          ? `${afastamento.dias_restantes_ate_pericia} ${idioma === "en" ? "day(s) until medical review" : "dia(s) até a revisão médica"}`
          : idioma === "en"
            ? "Medical review completed"
            : "Revisão médica concluída",
      ],
    })
  }

  return (
    <div className="career-bars">
      <div className="career-bars__title">
        <p className="eyebrow">{idioma === "en" ? "Comparison" : "Comparação"}</p>
        <h3>{idioma === "en" ? "Time Worked and Leave" : "Tempo trabalhado e afastamento"}</h3>
      </div>

      <div className="timeline-graph timeline-graph--interactive">
        <ExibirTooltip tooltip={tooltip} />
        <svg
          aria-label="Leave and career timeline"
          className="timeline-graph__svg"
          preserveAspectRatio="none"
          viewBox={`0 0 ${largura} ${altura}`}
          role="img"
        >
          {/* Line: Worked Time (Effective) */}
          <line className="timeline-graph__axis" x1={margemX} x2={xHoje} y1={eixoY} y2={eixoY} style={{ stroke: "var(--accent)", strokeWidth: 4 }} />

          <circle cx={xHoje} cy={eixoY} r="5" style={{ fill: "var(--accent)" }} />
          <text className="timeline-graph__label timeline-graph__label--muted" textAnchor="end" x={xHoje} y={eixoY + 22}>{idioma === "en" ? "Today" : "Hoje"}</text>

          <circle cx={margemX} cy={eixoY} r="4" style={{ fill: "var(--accent)" }} />
          <text className="timeline-graph__label timeline-graph__label--muted" textAnchor="end" x={margemX - 10} y={eixoY + 4}>{idioma === "en" ? "Start" : "Início"}</text>

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
                  {afastamento.total_dias} {idioma === "en" ? "days" : "dias"}
                </text>
                <text
                  className={`timeline-graph__label timeline-graph__label--muted ${isAbove ? "timeline-graph__label--above" : "timeline-graph__label--below"}`}
                  textAnchor="middle"
                  x={x}
                  y={isAbove ? y + 8 : y + 48}
                >
                  {formatarData(afastamento.data_inicio, idioma)}
                </text>
              </g>
            )
          })}
        </svg>
      </div>
    </div>
  )
}

function rotuloFerias(tipo: "regular" | "premium", idioma: "pt-BR" | "en") {
  if (idioma === "en") {
    return tipo === "regular" ? "Regular vacation" : "Premium leave"
  }

  return tipo === "regular" ? "Férias regulamentares" : "Férias-prêmio"
}

function GraficoPizzaFerias({
  resumo,
  idioma,
}: {
  resumo: ResumoFerias
  idioma: "pt-BR" | "en"
}) {
  const total = Math.max(resumo.dias_totais_usados, 1)
  const tipos = Object.entries(resumo.dias_por_tipo)
    .filter(([, dias]) => dias > 0)
    .sort((a, b) => b[1] - a[1]) as Array<[keyof typeof CORES_FERIAS, number]>

  const fatias = tipos.reduce<Array<{ cor: string; inicio: number; fim: number }>>(
    (acumuladas, [tipo, dias]) => {
      const inicioAnterior = acumuladas.length > 0 ? acumuladas[acumuladas.length - 1].fim : 0
      const proporcao = (dias / total) * 100

      acumuladas.push({
        cor: CORES_FERIAS[tipo],
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
          <strong>{resumo.dias_totais_usados}</strong>
          <span>{idioma === "en" ? "vacation" : "ferias"}</span>
        </div>
      </div>
      <div className="pie-visual__legend">
        {tipos.map(([tipo, dias]) => (
          <div className="pie-visual__legend-item" key={tipo}>
            <span className="pie-visual__legend-dot" style={{ background: CORES_FERIAS[tipo] }} />
            <div>
              <strong>{rotuloFerias(tipo, idioma)}</strong>
              <span>{`${dias} ${idioma === "en" ? "day(s)" : "dia(s)"}`}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function rotuloArmazenamento(
  origem: HistoricoFuncionalAnalise["armazenamento_origem"],
  idioma: "pt-BR" | "en",
) {
  if (idioma === "en") {
    return "local storage"
  }

  return "storage local"
}

function rotuloProcessamento(
  origem: HistoricoFuncionalAnalise["processamento_origem"],
  idioma: "pt-BR" | "en",
) {
  if (idioma === "en") {
    return origem === "fila" ? "background queue" : "direct backend processing"
  }

  return origem === "fila" ? "fila em segundo plano" : "processamento direto no backend"
}

export function HistoricoFuncionalView({
  usuarioId,
  historicoInicial,
  modoDemo,
  onCreateAccount,
  criandoConta = false,
}: HistoricoFuncionalViewProps) {
  const { language, texts } = useLanguage()
  const t = texts.history
  const {
    arquivo,
    arquivoDownloadUrl,
    arquivoAfastamentos,
    arquivoFerias,
    anosCltAverbados,
    sexo,
    categoriaPrevidenciaria,
    dataNascimento,
    erro,
    mensagemProcessamento,
    historico,
    modoAtualizacaoHistorico,
    modoAnexoAfastamentos,
    modoAnexoFerias,
    iniciarAnexoAfastamentos,
    iniciarAnexoFerias,
    iniciarAtualizacaoHistorico,
    recarregarHistorico,
    selecionarArquivo,
    selecionarArquivoAfastamentos,
    selecionarArquivoFerias,
    setAnosCltAverbados,
    setDataNascimento,
    setSexo,
    setCategoriaPrevidenciaria,
    usarCltMaximo,
    enviarFormulario,
  } = useHistoricoFuncionalController({
    usuarioId,
    historicoInicial,
  })

  const painel = historico ?? historicoInicial
  const resumo = painel?.resumo_grafico
  const resumoAfastamentos = painel?.afastamentos_resumo
  const resumoFerias = painel?.ferias_resumo
  const afastamentoPericia = resumoAfastamentos?.dias_por_tipo.aguardando_resultado_conclusivo_de_exame_pericial ?? 0

  return (
    <section className="analysis-card card">
      <div className="analysis-header">
        <div className="analysis-header__title">
          <p className="eyebrow eyebrow--title">{t.title}</p>
          <h2>{t.title}</h2>
          <p className="analysis-header__subtitle">{t.subtitle}</p>
        </div>
        <span className="status-pill">{painel ? t.statusSaved : t.waitingForPdf}</span>
      </div>

      <div className="analysis-stack">
        <section className="upload-shell">
          <div className="upload-shell__header">
            <div>
              <p className="eyebrow">{t.documents}</p>
              <h3>{modoDemo ? t.demoDashboard : painel ? t.addDocuments : t.uploadDocuments}</h3>
            </div>

            {modoDemo ? <span className="status-pill">{t.viewOnly}</span> : null}
            {!modoDemo ? (
              <div className="upload-shell__actions">
                {!painel ? (
                  <button
                    className="ghost-button ghost-button--compact"
                    type="button"
                    onClick={iniciarAtualizacaoHistorico}
                  >
                    {t.uploadCareerHistory}
                  </button>
                ) : null}
                {painel ? (
                  <button
                    className="ghost-button ghost-button--compact"
                    type="button"
                    onClick={iniciarAnexoAfastamentos}
                  >
                    {t.attachLeaveRecords}
                  </button>
                ) : null}
                {painel ? (
                  <button
                    className="ghost-button ghost-button--compact"
                    type="button"
                    onClick={iniciarAnexoFerias}
                  >
                    {t.attachVacationRecords}
                  </button>
                ) : null}
                {painel ? (
                  <button
                    className="ghost-button ghost-button--compact"
                    type="button"
                    onClick={iniciarAtualizacaoHistorico}
                  >
                    {t.updateCareerHistory}
                  </button>
                ) : null}
                {arquivoDownloadUrl ? (
                  <a
                    className="ghost-button ghost-button--compact"
                    download={arquivo?.name ?? "historico-funcional.pdf"}
                    href={arquivoDownloadUrl}
                  >
                    {t.downloadPdf}
                  </a>
                ) : null}
              </div>
            ) : null}
          </div>

          {modoDemo ? (
            <div className="upload-shell__collapsed">
              <p className="helper">{t.demoDataLoaded}</p>
              <div className="actions-row">
                {onCreateAccount ? (
                  <button
                    className="ghost-button"
                    type="button"
                    onClick={onCreateAccount}
                    disabled={criandoConta}
                  >
                    {criandoConta ? t.opening : t.openAccount}
                  </button>
                ) : null}
              </div>
            </div>
          ) : !painel && !modoAtualizacaoHistorico ? (
            <div className="upload-shell__collapsed">
              <p className="helper">{t.clickUploadCareerHistory}</p>
              {erro ? <p className="error-box">{erro}</p> : null}
            </div>
          ) : modoAtualizacaoHistorico ? (
            <form className="upload-form" onSubmit={enviarFormulario}>
              <label className="field">
                <span>{t.careerHistoryPdf}</span>
                <input type="file" accept="application/pdf" onChange={selecionarArquivo} />
              </label>

              <div className="field-grid">
                <label className="field">
                  <span>{t.dateOfBirth}</span>
                  <input
                    type="date"
                    value={dataNascimento}
                    onChange={(evento) => setDataNascimento(evento.target.value)}
                    required
                  />
                </label>

                <label className="field">
                  <span>{t.sex}</span>
                  <select
                    value={sexo}
                    onChange={(evento) => setSexo(evento.target.value as "feminino" | "masculino")}
                    required
                  >
                    <option value="feminino">{t.female}</option>
                    <option value="masculino">{t.male}</option>
                  </select>
                </label>

                <label className="field">
                  <span>{t.recognizedCltYears}</span>
                  <input
                    type="number"
                    min={0}
                    max={10}
                    value={anosCltAverbados}
                    onChange={(evento) => setAnosCltAverbados(Number(evento.target.value))}
                  />
                </label>

                <label className="field">
                  <span>{t.retirementCategory}</span>
                  <select
                    value={categoriaPrevidenciaria}
                    onChange={(evento) =>
                      setCategoriaPrevidenciaria(
                        evento.target.value as "geral" | "professor" | "seguranca" | "saude_exposicao",
                      )
                    }
                    required
                  >
                    <option value="geral">{t.categoryGeneral}</option>
                    <option value="professor">{t.categoryTeacher}</option>
                    <option value="seguranca">{t.categorySecurity}</option>
                    <option value="saude_exposicao">{t.categoryHealthExposure}</option>
                  </select>
                </label>
              </div>

              <label className="field">
                <span>{t.leaveRecordsPdf}</span>
                <input type="file" accept="application/pdf" onChange={selecionarArquivoAfastamentos} />
              </label>

              {arquivoAfastamentos ? (
                <p className="helper">{`${t.selectedLeaveRecordsFile}: ${arquivoAfastamentos.name}`}</p>
              ) : null}

              <label className="field">
                <span>{t.vacationRecordsPdf}</span>
                <input type="file" accept="application/pdf" onChange={selecionarArquivoFerias} />
              </label>

              {arquivoFerias ? (
                <p className="helper">{`${t.selectedVacationRecordsFile}: ${arquivoFerias.name}`}</p>
              ) : null}

              <div className="upload-actions">
                <button className="ghost-button" type="button" onClick={usarCltMaximo}>
                  {t.fill10CltYears}
                </button>
              </div>

              <p className="helper">{t.upTo10CltYears}</p>

              {arquivo ? <p className="helper">{`${t.selectedFile}: ${arquivo.name}`}</p> : null}
              {usuarioId ? (
                <button className="ghost-button" type="button" onClick={() => void recarregarHistorico()}>
                  {t.reloadLastSaved}
                </button>
              ) : null}

              {mensagemProcessamento ? <p className="helper">{mensagemProcessamento}</p> : null}
              {erro ? <p className="error-box">{erro}</p> : null}
            </form>
          ) : painel && modoAnexoAfastamentos ? (
            <div className="upload-shell__collapsed upload-shell__collapsed--compact">
              <label className="field">
                <span>{t.leaveRecordsPdf}</span>
                <input type="file" accept="application/pdf" onChange={selecionarArquivoAfastamentos} />
              </label>

              {arquivoAfastamentos ? (
                <p className="helper">{`${t.selectedLeaveRecordsFile}: ${arquivoAfastamentos.name}`}</p>
              ) : (
                <p className="helper">{t.selectPdfToAttach}</p>
              )}

              {mensagemProcessamento ? <p className="helper">{mensagemProcessamento}</p> : null}
              {erro ? <p className="error-box">{erro}</p> : null}
            </div>
          ) : painel && modoAnexoFerias ? (
            <div className="upload-shell__collapsed upload-shell__collapsed--compact">
              <label className="field">
                <span>{t.vacationRecordsPdf}</span>
                <input type="file" accept="application/pdf" onChange={selecionarArquivoFerias} />
              </label>

              {arquivoFerias ? (
                <p className="helper">{`${t.selectedVacationRecordsFile}: ${arquivoFerias.name}`}</p>
              ) : (
                <p className="helper">{t.selectVacationPdfToAttach}</p>
              )}

              {mensagemProcessamento ? <p className="helper">{mensagemProcessamento}</p> : null}
              {erro ? <p className="error-box">{erro}</p> : null}
            </div>
          ) : (
            <div className="upload-shell__collapsed">
              <p className="helper">{t.sendOtherFiles}</p>
              {erro ? <p className="error-box">{erro}</p> : null}
            </div>
          )}
        </section>

        {painel && resumo ? (
          <section className="overview-panel">
            <div className="overview-panel__chart">
              <GraficoPizzaTempo
                percentualTrabalhado={resumo.percentual_trabalhado}
                idioma={language}
              />
              {resumoAfastamentos ? <GraficoPizzaAfastamentos resumo={resumoAfastamentos} idioma={language} /> : null}
              {resumoFerias ? <GraficoPizzaFerias resumo={resumoFerias} idioma={language} /> : null}
            </div>

            <div className="overview-panel__content">
              <p className="helper">
                {`${t.pdfStorage}: ${rotuloArmazenamento(painel.armazenamento_origem, language)}.`}
              </p>
              <p className="helper">
                {`${t.processing}: ${rotuloProcessamento(painel.processamento_origem, language)}.`}
              </p>
              <div className="metric-strip">
                <div className="metric-line">
                  <span>{t.timeWorked}</span>
                  <strong>{formatarDuracaoEmAnos(resumo.tempo_trabalhado_dias, language)}</strong>
                </div>
                <div className="metric-line">
                  <span>{t.timeRemaining}</span>
                  <strong>{formatarDuracaoEmAnos(resumo.tempo_restante_dias, language)}</strong>
                </div>
                <div className="metric-line">
                  <span>{t.events}</span>
                  <strong>{resumo.eventos_totais}</strong>
                </div>
                {resumoAfastamentos ? (
                  <div className="metric-line metric-line--danger">
                    <span>{t.daysAway}</span>
                    <strong>{resumoAfastamentos.dias_totais}</strong>
                  </div>
                ) : null}
                {resumoAfastamentos ? (
                  <div className="metric-line metric-line--danger">
                    <span>{t.medicalReview}</span>
                    <strong>{afastamentoPericia}</strong>
                  </div>
                ) : null}
                {resumoFerias ? (
                  <div className="metric-line">
                    <span>{t.vacationDaysUsed}</span>
                    <strong>{resumoFerias.dias_totais_usados}</strong>
                  </div>
                ) : null}
                {resumoFerias ? (
                  <div className="metric-line">
                    <span>{t.nextVacation}</span>
                    <strong>
                      {resumoFerias.proxima_ferias_inicio
                        ? `${formatarData(resumoFerias.proxima_ferias_inicio, language)} - ${formatarData(resumoFerias.proxima_ferias_fim, language)}`
                        : "-"}
                    </strong>
                  </div>
                ) : null}
                <div className="metric-line">
                  <span>{t.nextProgression}</span>
                  <strong>{formatarData(painel.proxima_progressao_prevista, language)}</strong>
                </div>
                <div className="metric-line">
                  <span>{t.nextPromotion}</span>
                  <strong>{formatarData(painel.proxima_promocao_prevista, language)}</strong>
                </div>
              </div>

            </div>
          </section>
        ) : (
          <div className="history-empty">
            <p>{t.uploadHint}</p>
            <p>{t.loadedInDemo}</p>
          </div>
        )}

        {painel && resumo ? (
          <section className="timeline-panel">
          <div className="career-bars__title" style={{ marginBottom: "1.5rem" }}>
              <p className="eyebrow">{t.chartTitle}</p>
            </div>

            <LinhaDoTempoGrafica eventos={painel.eventos} idioma={language} />

            <GraficoComparativoTempo
              painel={painel}
              idioma={language}
            />
          </section>
        ) : null}

        {painel?.ferias?.length ? (
          <section className="timeline-panel">
            <div className="career-bars__title" style={{ marginBottom: "1rem" }}>
              <p className="eyebrow">{t.vacationHistory}</p>
              <h3>{t.vacationPeriods}</h3>
            </div>

            <div className="metric-strip">
              {painel.ferias
                .slice()
                .sort((a, b) => new Date(`${b.data_inicio}T00:00:00`).getTime() - new Date(`${a.data_inicio}T00:00:00`).getTime())
                .map((periodo) => (
                  <div
                    className="metric-line"
                    key={`${periodo.tipo}-${periodo.data_inicio}-${periodo.data_fim}`}
                  >
                    <span>{rotuloFerias(periodo.tipo, language)}</span>
                    <strong>{`${formatarData(periodo.data_inicio, language)} - ${formatarData(periodo.data_fim, language)}`}</strong>
                    <small>
                      {`${periodo.dias_contabilizados} ${
                        periodo.regra_contagem === "dias_uteis" ? t.businessDays : t.calendarDays
                      }`}
                    </small>
                  </div>
                ))}
            </div>
          </section>
        ) : null}
      </div>
    </section>
  )
}




