export type HistoricoFuncionalUpload = FormData

export type AfastamentosUpload = FormData
export type FeriasUpload = FormData

export type JobAgendadoResponse = {
  job_id: string
  status: "queued"
  detail: string | null
}

export type JobStatusResponse<T> = {
  job_id: string
  status: "queued" | "started" | "finished" | "failed"
  result: T | null
  detail: string | null
}

export type AfastamentoPeriodo = {
  tipo: "aguardando_resultado_conclusivo_de_exame_pericial" | "licenca_para_tratamento_de_saude"
  data_inicio: string
  data_fim: string
  total_dias: number
  legislacao: string | null
  publicacao: string | null
  mes_ano_afastamento: string
  dias_restantes_ate_pericia: number
}

export type AfastamentoResumo = {
  periodos_totais: number
  dias_totais: number
  dias_por_tipo: Record<string, number>
  periodos_por_tipo: Record<string, number>
}

export type FeriasPeriodo = {
  tipo: "regular" | "premium"
  data_inicio: string
  data_fim: string
  dias_contabilizados: number
  dias_corridos: number
  regra_contagem: "dias_uteis" | "dias_corridos"
  observacao: string | null
}

export type FeriasResumo = {
  periodos_totais: number
  dias_totais_usados: number
  dias_por_tipo: Record<string, number>
  periodos_por_tipo: Record<string, number>
  proxima_ferias_inicio: string | null
  proxima_ferias_fim: string | null
  proxima_ferias_tipo: "regular" | "premium" | null
}

export type HistoricoFuncionalEvento = {
  tipo: "nomeacao" | "progressao" | "promocao" | "substituicao"
  descricao: string
  cargo: string
  simbolo: string
  nivel: string
  grau: string
  data_publicacao: string
  data_efetiva: string
  data_prevista: string | null
  status: "cumprindo" | "atrasado" | "nao_aplicavel" | "estagio_probatorio"
  atraso_dias: number
}

export type HistoricoFuncionalResumoAposentadoria = {
  tempo_restante_dias: number
  idade_na_aposentadoria_anos: number
  idade_por_tempo_servico_anos: number
  idade_minima_governo_anos: number
  data_por_tempo_servico: string
  data_por_idade_minima: string
  data_prevista: string
  nivel_previsto: string
  grau_previsto: string
  observacao: string
}

export type HistoricoFuncionalAnalise = {
  historico_id: number
  usuario_id: number | null
  arquivo_nome: string
  nome: string
  masp: string
  cpf: string | null
  data_emissao: string | null
  data_nascimento: string
  sexo: "feminino" | "masculino" | null
  categoria_previdenciaria: "geral" | "professor" | "seguranca" | "saude_exposicao" | null
  data_posse: string
  data_exercicio: string
  cargo_atual: string
  simbolo_atual: string
  nivel_atual: string
  grau_atual: string
  tempo_clt_averbado_anos: number
  tempo_clt_creditado_anos: number
  data_aposentadoria_por_carreira: string
  data_aposentadoria_por_idade: string
  data_aposentadoria_prevista: string
  dias_trabalhados: number
  dias_totais_ate_aposentadoria: number
  percentual_trabalhado: number
  percentual_restante: number
  proxima_progressao_prevista: string
  proxima_promocao_prevista: string
  resumo_grafico: {
    tempo_trabalhado_dias: number
    tempo_restante_dias: number
    percentual_trabalhado: number
    percentual_restante: number
    eventos_totais: number
    eventos_por_status: Record<string, number>
    eventos_por_tipo: Record<string, number>
  }
  resumo_aposentadoria: HistoricoFuncionalResumoAposentadoria | null
  afastamentos_arquivo_nome: string | null
  afastamentos_resumo: AfastamentoResumo | null
  afastamentos: AfastamentoPeriodo[]
  ferias_arquivo_nome: string | null
  ferias_resumo: FeriasResumo | null
  ferias: FeriasPeriodo[]
  eventos: HistoricoFuncionalEvento[]
  armazenamento_origem: "local"
  processamento_origem: "fila" | "direto"
}

export function formatarTipoEvento(tipo: HistoricoFuncionalEvento["tipo"], idioma: "pt-BR" | "en" = "pt-BR") {
  if (idioma === "en") {
    switch (tipo) {
      case "nomeacao":
        return "Appointment"
      case "progressao":
        return "Progression"
      case "promocao":
        return "Promotion"
      default:
        return "Substitution"
    }
  }

  switch (tipo) {
    case "nomeacao":
      return "Nomeação"
    case "progressao":
      return "Progressão"
    case "promocao":
      return "Promoção"
    default:
      return "Substituição"
  }
}
