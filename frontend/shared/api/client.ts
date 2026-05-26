type RespostaErroApi = {
  detail?: string
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL?.trim()?.replace(/\/$/, "")

export class ApiResponseError extends Error {
  status: number
  url: string

  constructor(response: Response, mensagemPadrao: string) {
    super(mensagemPadrao)
    this.name = "ApiResponseError"
    this.status = response.status
    this.url = response.url || "unknown"
  }
}

function montarUrlApi(path: string) {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path
  }

  if (!API_BASE_URL) {
    throw new Error("NEXT_PUBLIC_API_URL nao foi definido.")
  }

  const caminho = path.startsWith("/") ? path : `/${path}`
  return new URL(caminho, API_BASE_URL).toString()
}

export async function apiFetch(path: string, init: RequestInit = {}) {
  const url = montarUrlApi(path)
  try {
    return await fetch(url, {
      ...init,
      credentials: init.credentials ?? "include",
    })
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw error
    }

    throw new Error("We could not load the information right now. Please try again in a moment.")
  }
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
    throw new ApiResponseError(response, mensagem)
  }

  return dados as T
}
