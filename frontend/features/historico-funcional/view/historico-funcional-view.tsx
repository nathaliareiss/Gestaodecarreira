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

  if (status === "estagio_probatorio") {
    return "Em estágio probatório"
  }

  return "Não aplicável"
}

function statusClass(status: HistoricoFuncionalAnalise["eventos"][number]["status"]) {
  if (status === "atrasado") {
    return "timeline-badge timeline-badge--danger"
  }

  if (status === "cumprindo") {
    return "timeline-badge timeline-badge--success"
  }

  if (status === "estagio_probatorio") {
    return "timeline-badge timeline-badge--warning"
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
          <p className="eyebrow">Histórico funcional</p>
          <h2>Cálculos de carreira e leitura do PDF</h2>
        </div>
        <span className="status-pill">{painel ? "salvo" : "aguardando PDF"}</span>
      </div>

      <div className="upload-grid">
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
              Recarregar último salvo
            </button>
          ) : null}

          {erro ? <p className="error-box">{erro}</p> : null}
        </form>

        <div className="summary-panel">
          <p className="eyebrow">Cenários calculados</p>
          {painel ? (
            <>
              <div className="summary-grid">
                <article className="metric-card">
                  <span className="label">Tempo trabalhado</span>
                  <strong>{formatarDuracaoEmAnos(painel.dias_trabalhados)}</strong>
                  <p>{formatarPorcentagem(painel.percentual_trabalhado)} concluído</p>
                </article>
                <article className="metric-card">
                  <span className="label">Tempo restante</span>
                  <strong>{formatarDuracaoEmAnos(Math.max(painel.dias_totais_ate_aposentadoria - painel.dias_trabalhados, 0))}</strong>
                  <p>{formatarPorcentagem(painel.percentual_restante)} restante</p>
                </article>
                <article className="metric-card">
                  <span className="label">Aposentadoria prevista</span>
                  <strong>{formatarData(painel.data_aposentadoria_prevista)}</strong>
                  <p>Carreira ou idade, o que vier por último.</p>
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
                    <span>Tempo de serviço até aposentar</span>
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
                  <span className="label">Próxima progressão</span>
                  <strong>{formatarData(painel.proxima_progressao_prevista)}</strong>
                </article>
                <article className="metric-card">
                  <span className="label">Próxima promoção</span>
                  <strong>{formatarData(painel.proxima_promocao_prevista)}</strong>
                </article>
                <article className="metric-card">
                  <span className="label">Cargo atual</span>
                  <strong>{painel.cargo_atual}</strong>
                </article>
                <article className="metric-card">
                  <span className="label">Símbolo atual</span>
                  <strong>
                    {painel.simbolo_atual} {painel.nivel_atual} {painel.grau_atual}
                  </strong>
                </article>
              </div>
            </>
          ) : (
            <div className="history-empty">
              <p>
                Envie o PDF do histórico funcional para o sistema ler os dados, salvar
                no banco e montar os cálculos de carreira.
              </p>
              <p>
                Aqui você vai ver o tempo de trabalho, a previsão de aposentadoria e a
                próxima progressão e promoção.
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
