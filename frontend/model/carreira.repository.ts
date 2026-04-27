import type { CadastroCarreira, ResumoCarreira } from "./carreira.model"

export function obterApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
}

export async function buscarResumoCarreira(
  cadastro: CadastroCarreira,
): Promise<ResumoCarreira> {
  const response = await fetch(`${obterApiBaseUrl()}/api/carreira/resumo`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(cadastro),
  })

  const dados = (await response.json()) as ResumoCarreira | { detail?: string }

  if (!response.ok) {
    const mensagem =
      dados && "detail" in dados ? dados.detail ?? "Erro ao calcular" : "Erro ao calcular"
    throw new Error(mensagem)
  }

  return dados as ResumoCarreira
}

