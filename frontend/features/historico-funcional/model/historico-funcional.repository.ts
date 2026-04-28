import { obterApiBaseUrl } from "@/shared/config/api"

import type {
  HistoricoFuncionalAnalise,
  HistoricoFuncionalUpload,
} from "./historico-funcional.model"

type RespostaErroApi = {
  detail?: string
}

async function lerResposta<T>(response: Response, mensagemPadrao: string): Promise<T> {
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

export async function analisarHistoricoFuncional(
  payload: HistoricoFuncionalUpload,
): Promise<HistoricoFuncionalAnalise> {
  const response = await fetch(`${obterApiBaseUrl()}/api/historicos-funcionais/analisar`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  return lerResposta<HistoricoFuncionalAnalise>(response, "Erro ao analisar o historico funcional")
}

export async function buscarUltimoHistoricoFuncional(
  usuarioId: number,
): Promise<HistoricoFuncionalAnalise | null> {
  const response = await fetch(
    `${obterApiBaseUrl()}/api/historicos-funcionais/usuario/${usuarioId}/ultimo`,
    {
      method: "GET",
    },
  )

  if (response.status === 404) {
    return null
  }

  return lerResposta<HistoricoFuncionalAnalise>(
    response,
    "Erro ao carregar o historico funcional",
  )
}

