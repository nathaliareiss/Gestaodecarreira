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
            <strong>{formatarDataISO(resumo.data_nascimento)}</strong>
          </div>
          <div className="result-block">
            <span className="label">Ingresso</span>
            <strong>{formatarDataISO(resumo.data_ingresso)}</strong>
          </div>
          <div className="result-block">
            <span className="label">CLT averbado</span>
            <strong>{formatarSimNao(resumo.tem_tempo_clt_averbado)}</strong>
          </div>
          <div className="result-block">
            <span className="label">25 anos de carreira</span>
            <strong>{formatarDataISO(resumo.data_25_anos_carreira)}</strong>
          </div>
          <div className="result-block">
            <span className="label">Idade nessa data</span>
            <strong>{resumo.idade_na_data_25_anos_carreira} anos</strong>
          </div>
          <div className="result-block">
            <span className="label">Idade mínima</span>
            <strong>{formatarDataISO(resumo.data_idade_minima_aposentadoria)}</strong>
          </div>
          <div className="result-block">
            <span className="label">Pode aposentar</span>
            <strong>{formatarSimNao(resumo.possui_idade_minima_na_data_25_anos_carreira)}</strong>
          </div>
          <div className="result-block">
            <span className="label">Aposentadoria provável</span>
            <strong>{formatarDataISO(resumo.data_prevista_aposentadoria)}</strong>
          </div>
          <div className="result-block">
            <span className="label">Grau aos 45</span>
            <strong>
              {resumo.grau_aos_45_anos} / Nível {resumo.nivel_aos_45_anos}
            </strong>
          </div>
          <div className="result-block">
            <span className="label">Grau na aposentadoria</span>
            <strong>
              {resumo.grau_na_aposentadoria} / Nível {resumo.nivel_na_aposentadoria}
            </strong>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <p>
            Preencha o formulário e clique em <strong>Calcular resumo</strong> para ver
            os resultados.
          </p>
        </div>
      )}
    </section>
  )
}

