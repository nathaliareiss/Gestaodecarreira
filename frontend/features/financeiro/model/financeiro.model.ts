export type ValorFinanceiro = string | number | null | undefined

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
