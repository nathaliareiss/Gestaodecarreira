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
  salario_base_referencia_anual: number
  bruto_total_referencia_anual: number
  liquido_referencia_anual: number
  descontos_referencia_anual: number
  vantagens_adicionais_referencia_anual: number
  composicao_vantagens_referencia_anual: Record<string, number>
  composicao_descontos_referencia_anual: Record<string, number>
  quantidade_contracheques: number
  variacao_percentual_salario_base_ano_a_ano: number | null
  crescimento_relevante: boolean
}

export type FinanceiroEvolucaoSalarialResponse = {
  batch_id: number
  ano_inicial: number
  ano_final: number
  salario_base_inicial_referencia: number
  salario_base_final_referencia: number
  bruto_total_inicial_referencia: number
  bruto_total_final_referencia: number
  liquido_inicial_referencia: number
  liquido_final_referencia: number
  descontos_inicial_referencia: number
  descontos_final_referencia: number
  vantagens_adicionais_inicial_referencia: number
  vantagens_adicionais_final_referencia: number
  variacao_acumulada_salario_base_percentual: number
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
