export type ValorFinanceiro = string | number | null | undefined

export type FinanceiroBatchStatus = "pending" | "processing" | "completed" | "failed"

export type FinanceiroBatchUploadResponse = {
  batch_id: number
  status: FinanceiroBatchStatus
}

export type FinanceiroBatchStatusResponse = {
  total: number
  processed: number
  failed: number
  status: FinanceiroBatchStatus
}

export type FinanceiroEvolucaoSalarialSerieItem = {
  ano: number
  bruto_referencia_anual: number
  liquido_referencia_anual: number
  descontos_referencia_anual: number
  quantidade_contracheques: number
  variacao_percentual_bruto_ano_a_ano: number | null
  variacao_percentual_liquido_ano_a_ano: number | null
  crescimento_relevante: boolean
}

export type FinanceiroEvolucaoSalarialResponse = {
  batch_id: number
  ano_inicial: number
  ano_final: number
  bruto_inicial_referencia: number
  bruto_final_referencia: number
  liquido_inicial_referencia: number
  liquido_final_referencia: number
  descontos_inicial_referencia: number
  descontos_final_referencia: number
  variacao_acumulada_bruto_percentual: number
  variacao_acumulada_liquido_percentual: number
  cagr_bruto_percentual: number
  cagr_liquido_percentual: number
  anos_sem_crescimento_relevante: number[]
  series: FinanceiroEvolucaoSalarialSerieItem[]
}

export type ContrachequeAnalise = {
  competencia: string
  ano: number
  mes: number
  bruto: ValorFinanceiro
  descontos: ValorFinanceiro
  liquido: ValorFinanceiro
  vencimento_basico: ValorFinanceiro
  adicional_desempenho: ValorFinanceiro
  adicional_noturno: ValorFinanceiro
  irrf: ValorFinanceiro
  previdencia: ValorFinanceiro
}
