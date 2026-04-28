"use client"

import { useHistoricoFuncionalController } from "../controller/use-historico-funcional-controller"
import { formatarTipoEvento, type HistoricoFuncionalAnalise } from "../model/historico-funcional.model"

type HistoricoFuncionalViewProps = {
  usuarioId: number | null
  historicoInicial: HistoricoFuncionalAnalise | null
}

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

function statusLabel(status: HistoricoFuncionalAnalise["eventos"][number]["status"]) {
  if (status === "atrasado") {
    return "Atrasado"
  }

  if (status === "cumprindo") {
    return "Cumprindo"
  }

  return "Nao aplicavel"
}

function statusClass(status: HistoricoFuncionalAnalise["eventos"][number]["status"]) {
  if (status === "atrasado") {
    return "timeline-badge timeline-badge--danger"
  }

  if (status === "cumprindo") {
    return "timeline-badge timeline-badge--success"
  }

  return "timeline-badge timeline-badge--neutral"
}

export function HistoricoFuncionalView({
  usuarioId,
  historicoInicial,
}: HistoricoFuncionalViewProps) {
  const {
    arquivo,
    anosCltAverbados,
    carregando,
    dataNascimento,
    erro,
    historico,
    recarregarHistorico,
    selecionarArquivo,
    setAnosCltAverbados,
    setDataNascimento,
    usarCltMaximo,
    enviarFormulario,
  } = useHistoricoFuncionalController({
    usuarioId,
    historicoInicial,
  })

  const painel = historico ?? historicoInicial

  return (
    <section className="analysis-card card">
      <div className="card-header">
        <div>
          <p className="eyebrow">Historico funcional</p>
          <h2>Calculos de carreira e leitura do PDF</h2>
        </div>
        <span className="status-pill">{painel ? "salvo" : "aguardando pdf"}</span>
      </div>

      <div className="upload-grid">
        <form className="upload-form" onSubmit={enviarFormulario}>
          <label className="field">
            <span>PDF do historico funcional</span>
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

          <div className="upload-actions">
            <button className="ghost-button" type="button" onClick={usarCltMaximo}>
              Preencher 10 anos de CLT
            </button>
            <button className="primary-button" type="submit" disabled={carregando}>
              {carregando ? "Analisando..." : "Analisar e salvar PDF"}
            </button>
          </div>

          <p className="helper">
            O sistema limita a CLT em 10 anos. Se a pessoa tiver esse tempo, basta
            preencher `10` ou usar o atalho.
          </p>

          {arquivo ? <p className="helper">Arquivo selecionado: {arquivo.name}</p> : null}
          {usuarioId ? (
            <button className="ghost-button" type="button" onClick={() => void recarregarHistorico()}>
              Recarregar ultimo salvo
            </button>
          ) : null}

          {erro ? <p className="error-box">{erro}</p> : null}
        </form>

        <div className="summary-panel">
          <p className="eyebrow">Cenarios calculados</p>
          {painel ? (
            <>
              <div className="summary-grid">
                <article className="metric-card">
                  <span className="label">Tempo trabalhado</span>
                  <strong>{formatarDuracaoEmAnos(painel.dias_trabalhados)}</strong>
                  <p>{formatarPorcentagem(painel.percentual_trabalhado)} concluido</p>
                </article>
                <article className="metric-card">
                  <span className="label">Tempo restante</span>
                  <strong>{formatarDuracaoEmAnos(Math.max(painel.dias_totais_ate_aposentadoria - painel.dias_trabalhados, 0))}</strong>
                  <p>{formatarPorcentagem(painel.percentual_restante)} restante</p>
                </article>
                <article className="metric-card">
                  <span className="label">Aposentadoria prevista</span>
                  <strong>{formatarData(painel.data_aposentadoria_prevista)}</strong>
                  <p>Carreira ou idade, o que vier por ultimo.</p>
                </article>
                <article className="metric-card">
                  <span className="label">CLT averbada</span>
                  <strong>{painel.tempo_clt_creditado_anos} de 10 anos</strong>
                  <p>{painel.tempo_clt_averbado_anos} informados no upload.</p>
                </article>
              </div>

              <div className="progress-list">
                <div className="progress-row">
                  <div className="progress-row-header">
                    <span>Tempo de servico ate aposentar</span>
                    <strong>{formatarPorcentagem(painel.percentual_trabalhado)}</strong>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill" style={{ width: `${painel.percentual_trabalhado}%` }} />
                  </div>
                </div>
                <div className="progress-row">
                  <div className="progress-row-header">
                    <span>Tempo de CLT aproveitado</span>
                    <strong>{painel.tempo_clt_creditado_anos} / 10 anos</strong>
                  </div>
                  <div className="progress-track">
                    <div className="progress-fill progress-fill--accent" style={{ width: `${(painel.tempo_clt_creditado_anos / 10) * 100}%` }} />
                  </div>
                </div>
              </div>

              <div className="summary-grid summary-grid--dense">
                <article className="metric-card">
                  <span className="label">Proxima progressao</span>
                  <strong>{formatarData(painel.proxima_progressao_prevista)}</strong>
                </article>
                <article className="metric-card">
                  <span className="label">Proxima promocao</span>
                  <strong>{formatarData(painel.proxima_promocao_prevista)}</strong>
                </article>
                <article className="metric-card">
                  <span className="label">Cargo atual</span>
                  <strong>{painel.cargo_atual}</strong>
                </article>
                <article className="metric-card">
                  <span className="label">Simbolo atual</span>
                  <strong>
                    {painel.simbolo_atual} {painel.nivel_atual} {painel.grau_atual}
                  </strong>
                </article>
              </div>
            </>
          ) : (
            <div className="history-empty">
              <p>
                Envie o PDF do historico funcional para o sistema ler os dados, salvar
                no banco e montar os calculos de carreira.
              </p>
              <p>
                Aqui voce vai ver o tempo de trabalho, a previsao de aposentadoria e a
                proxima progressao e promocao.
              </p>
            </div>
          )}
        </div>
      </div>

      {painel ? (
        <div className="timeline-panel">
          <div className="card-header">
            <div>
              <p className="eyebrow">Linha do tempo</p>
              <h2>Quando deveria acontecer e quando aconteceu</h2>
            </div>
          </div>

          <div className="table-wrap">
            <table className="timeline-table">
              <thead>
                <tr>
                  <th>Evento</th>
                  <th>Previsto</th>
                  <th>Efetivado</th>
                  <th>Status</th>
                  <th>Atraso</th>
                </tr>
              </thead>
              <tbody>
                {painel.eventos.map((evento) => (
                  <tr key={`${evento.tipo}-${evento.data_efetiva}-${evento.descricao}`}>
                    <td>
                      <strong>{formatarTipoEvento(evento.tipo)}</strong>
                      <span>{evento.cargo}</span>
                    </td>
                    <td>{formatarData(evento.data_prevista)}</td>
                    <td>{formatarData(evento.data_efetiva)}</td>
                    <td>
                      <span className={statusClass(evento.status)}>{statusLabel(evento.status)}</span>
                    </td>
                    <td>{evento.atraso_dias > 0 ? `${evento.atraso_dias} dias` : "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </section>
  )
}

