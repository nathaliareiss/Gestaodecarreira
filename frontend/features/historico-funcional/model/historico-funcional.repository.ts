import type {
  AfastamentosUpload,
  HistoricoFuncionalAnalise,
  HistoricoFuncionalUpload,
} from "./historico-funcional.model"
import { apiFetch, parseApiResponse } from "@/shared/api/client"

export async function analisarHistoricoFuncional(
  payload: HistoricoFuncionalUpload,
): Promise<HistoricoFuncionalAnalise> {
  const response = await apiFetch("/api/historicos-funcionais/analisar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  return parseApiResponse<HistoricoFuncionalAnalise>(
    response,
    "Erro ao analisar o histórico funcional.",
  )
}

export async function buscarUltimoHistoricoFuncional(
  usuarioId: number,
): Promise<HistoricoFuncionalAnalise | null> {
  const response = await apiFetch(`/api/historicos-funcionais/usuario/${usuarioId}/ultimo`, {
    method: "GET",
  })

  if (response.status === 404) {
    return null
  }

  return parseApiResponse<HistoricoFuncionalAnalise>(
    response,
    "Erro ao carregar o histórico funcional.",
  )
}

export async function anexarAfastamentosAoHistorico(
  usuarioId: number,
  payload: AfastamentosUpload,
): Promise<HistoricoFuncionalAnalise> {
  const response = await apiFetch(`/api/historicos-funcionais/usuario/${usuarioId}/afastamentos`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  return parseApiResponse<HistoricoFuncionalAnalise>(
    response,
    "Erro ao analisar o arquivo de afastamentos.",
  )
}
