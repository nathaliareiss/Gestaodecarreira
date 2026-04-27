import type {
  CadastroCarreiraRequest,
  ResumoCarreiraResponse,
} from "./carreira.types"

export function obterApiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
}

export async function buscarResumoCarreira(
  cadastro: CadastroCarreiraRequest,
): Promise<ResumoCarreiraResponse> {
  const response = await fetch(`${obterApiBaseUrl()}/api/carreira/resumo`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(cadastro),
  })

  const dados = (await response.json()) as
    | ResumoCarreiraResponse
    | { detail?: string }

  if (!response.ok) {
    const mensagem =
      dados && "detail" in dados ? dados.detail ?? "Erro ao calcular" : "Erro ao calcular"
    throw new Error(mensagem)
  }

  return dados as ResumoCarreiraResponse
}

