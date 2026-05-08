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
  valor_bruto_medio: number
  quantidade_contracheques: number
}

export type FinanceiroEvolucaoSalarialResponse = {
  batch_id: number
  ano_inicial: number
  ano_final: number
  valor_inicial: number
  valor_final: number
  variacao_absoluta: number
  variacao_percentual: number
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
