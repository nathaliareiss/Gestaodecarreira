export type HistoricoFuncionalUpload = {
  usuario_id: number | null
  arquivo_nome: string
  arquivo_base64: string
  data_nascimento: string
  anos_clt_averbados: number
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
  status: "cumprindo" | "atrasado" | "nao_aplicavel"
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
  eventos: HistoricoFuncionalEvento[]
}

export function formatarTipoEvento(tipo: HistoricoFuncionalEvento["tipo"]) {
  if (tipo === "nomeacao") {
    return "Nomeação"
  }

  if (tipo === "progressao") {
    return "Progressão"
  }

  if (tipo === "promocao") {
    return "Promoção"
  }

  return "Substituição"
}

