export type ValorFinanceiro = string | number | null | undefined

export type FinanceiroBatchStatus = "pending" | "processing" | "completed" | "failed"

export type FinanceiroBatchUploadResponse = {
  batch_id: number
  status: FinanceiroBatchStatus
}

export type FinanceiroBatchStatusResponse = {
  total: number
  processed_count: number
  duplicated_count: number
  failed_count: number
  status: FinanceiroBatchStatus
  last_error_message: string | null
  failure_messages: string[]
  processed?: number
  duplicated?: number
  failed?: number
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
  batch_id: number | null
  ano_inicial: number | null
  ano_final: number | null
  salario_base_inicial_referencia: number | null
  salario_base_final_referencia: number | null
  bruto_total_inicial_referencia: number | null
  bruto_total_final_referencia: number | null
  liquido_inicial_referencia: number | null
  liquido_final_referencia: number | null
  descontos_inicial_referencia: number | null
  descontos_final_referencia: number | null
  vantagens_adicionais_inicial_referencia: number | null
  vantagens_adicionais_final_referencia: number | null
  variacao_acumulada_salario_base_percentual: number | null
  anos_sem_crescimento_relevante: number[]
  series: FinanceiroEvolucaoSalarialSerieItem[]
}

export type FinanceiroContrachequeResumo = {
  id: number
  competencia: string
  ano: number
  mes: number
  salario_base: number
  bruto_total: number
  liquido: number
  descontos: number
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
