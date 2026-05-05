import { obterApiBaseUrl } from "@/shared/config/api"

type RespostaErroApi = {
  detail?: string
}

export async function apiFetch(path: string, init: RequestInit = {}) {
  const caminho = path.startsWith("/") ? path : `/${path}`
  return fetch(`${obterApiBaseUrl()}${caminho}`, init)
}

export async function parseApiResponse<T>(
  response: Response,
  mensagemPadrao: string,
): Promise<T> {
  const dados = (await response.json().catch(() => null)) as T | RespostaErroApi | null

  if (!response.ok) {
    const mensagem =
      dados && typeof dados === "object" && "detail" in dados
        ? dados.detail ?? mensagemPadrao
        : mensagemPadrao
    throw new Error(mensagem)
  }

  return dados as T
}
