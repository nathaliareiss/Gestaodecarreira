import type { ResumoCarreira } from "../model/carreira.model"
import { formatarDataISO, formatarSimNao } from "./carreira.formatters"

type CarreiraResultsViewProps = {
  resumo: ResumoCarreira | null
}

export function CarreiraResultsView({ resumo }: CarreiraResultsViewProps) {
  return (
    <section className="card results-card">
      <div className="card-header">
        <div>
          <p className="eyebrow">Result</p>
          <h2>Career Summary</h2>
        </div>
        <span className="status-pill">{resumo ? "Received" : "Waiting"}</span>
      </div>

      {resumo ? (
        <div className="results-grid">
          <div className="result-block">
            <span className="label">Name</span>
            <strong>{resumo.nome}</strong>
          </div>
          <div className="result-block">
            <span className="label">Birth</span>
            <strong>{formatarDataISO(resumo.data_nascimento)}</strong>
          </div>
          <div className="result-block">
            <span className="label">Join Date</span>
            <strong>{formatarDataISO(resumo.data_ingresso)}</strong>
          </div>
          <div className="result-block">
            <span className="label">Recognized CLT</span>
            <strong>{formatarSimNao(resumo.tem_tempo_clt_averbado)}</strong>
          </div>
          <div className="result-block">
            <span className="label">25 Years of Career</span>
            <strong>{formatarDataISO(resumo.data_25_anos_carreira)}</strong>
          </div>
          <div className="result-block">
            <span className="label">Age at That Date</span>
            <strong>{resumo.idade_na_data_25_anos_carreira} years</strong>
          </div>
          <div className="result-block">
            <span className="label">Minimum Age</span>
            <strong>{formatarDataISO(resumo.data_idade_minima_aposentadoria)}</strong>
          </div>
          <div className="result-block">
            <span className="label">Can Retire</span>
            <strong>{formatarSimNao(resumo.possui_idade_minima_na_data_25_anos_carreira)}</strong>
          </div>
          <div className="result-block">
            <span className="label">Projected Retirement</span>
            <strong>{formatarDataISO(resumo.data_prevista_aposentadoria)}</strong>
          </div>
          <div className="result-block">
            <span className="label">Grade at 45</span>
            <strong>
              {resumo.grau_aos_45_anos} / Level {resumo.nivel_aos_45_anos}
            </strong>
          </div>
          <div className="result-block">
            <span className="label">Grade at Retirement</span>
            <strong>
              {resumo.grau_na_aposentadoria} / Level {resumo.nivel_na_aposentadoria}
            </strong>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <p>
            Fill out the form and click <strong>Calculate Summary</strong> to see the results.
          </p>
        </div>
      )}
    </section>
  )
}
