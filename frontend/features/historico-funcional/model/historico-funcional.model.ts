export type HistoricoFuncionalUpload = {
  usuario_id: number | null
  arquivo_nome: string
  arquivo_base64: string
  data_nascimento: string
  anos_clt_averbados: number
  afastamentos_arquivo_nome?: string | null
  afastamentos_arquivo_base64?: string | null
}

export type AfastamentosUpload = {
  arquivo_nome: string
  arquivo_base64: string
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

export type HistoricoFuncionalAnalise = {
  historico_id: number
  usuario_id: number | null
  arquivo_nome: string
  nome: string
  masp: string
  cpf: string | null
  data_emissao: string | null
  data_nascimento: string
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
  afastamentos_arquivo_nome: string | null
  afastamentos_resumo: AfastamentoResumo | null
  afastamentos: AfastamentoPeriodo[]
  eventos: HistoricoFuncionalEvento[]
}

export function formatarTipoEvento(tipo: HistoricoFuncionalEvento["tipo"]) {
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
