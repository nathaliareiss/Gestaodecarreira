import type {
  AfastamentosUpload,
  FeriasUpload,
  HistoricoFuncionalAnalise,
  HistoricoFuncionalUpload,
  JobAgendadoResponse,
  JobStatusResponse,
} from "./historico-funcional.model"
import { apiFetch, parseApiResponse } from "@/shared/api/client"

export async function analisarHistoricoFuncional(
  payload: HistoricoFuncionalUpload,
): Promise<HistoricoFuncionalAnalise | JobAgendadoResponse> {
  const response = await apiFetch("/api/historicos-funcionais/analisar", {
    method: "POST",
    body: payload,
  })

  return parseApiResponse<HistoricoFuncionalAnalise | JobAgendadoResponse>(
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
): Promise<HistoricoFuncionalAnalise | JobAgendadoResponse> {
  const response = await apiFetch(`/api/historicos-funcionais/usuario/${usuarioId}/afastamentos`, {
    method: "POST",
    body: payload,
  })

  return parseApiResponse<HistoricoFuncionalAnalise | JobAgendadoResponse>(
    response,
    "Erro ao analisar o arquivo de afastamentos.",
  )
}

export async function anexarFeriasAoHistorico(
  usuarioId: number,
  payload: FeriasUpload,
): Promise<HistoricoFuncionalAnalise | JobAgendadoResponse> {
  const response = await apiFetch(`/api/historicos-funcionais/usuario/${usuarioId}/ferias`, {
    method: "POST",
    body: payload,
  })

  return parseApiResponse<HistoricoFuncionalAnalise | JobAgendadoResponse>(
    response,
    "Erro ao analisar o arquivo de ferias.",
  )
}

export async function consultarStatusJobHistorico(
  jobId: string,
): Promise<JobStatusResponse<HistoricoFuncionalAnalise>> {
  const response = await apiFetch(`/api/historicos-funcionais/jobs/${jobId}`, {
    method: "GET",
  })

  return parseApiResponse<JobStatusResponse<HistoricoFuncionalAnalise>>(
    response,
    "Erro ao consultar o processamento.",
  )
}
