export function formatarDataISO(valor: string) {
  const [ano, mes, dia] = valor.split("-")
  return `${dia}/${mes}/${ano}`
}

export function formatarSimNao(valor: boolean) {
  return valor ? "Yes" : "No"
}
