import { obterApiBaseUrl } from "@/shared/config/api"

type RespostaErroApi = {
  detail?: string
}

function montarUrlApi(path: string) {
  const baseUrl = obterApiBaseUrl().replace(/\/$/, "")
  const caminho = path.startsWith("/") ? path : `/${path}`

  if (baseUrl.endsWith("/api") && caminho.startsWith("/api/")) {
    return `${baseUrl}${caminho.replace(/^\/api/, "")}`
  }

  return `${baseUrl}${caminho}`
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

    throw new Error(
      `We could not reach the backend API at ${url}. Check that it is running and that NEXT_PUBLIC_API_URL is correct.`,
    )
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
    throw new Error(`${mensagem} [URL: ${response.url || "unknown"}]`)
  }

  return dados as T
}
