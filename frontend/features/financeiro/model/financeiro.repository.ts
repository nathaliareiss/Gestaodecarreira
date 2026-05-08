import { apiFetch, parseApiResponse } from "@/shared/api/client"

import type {
  ContrachequeAnalise,
  FinanceiroContrachequeResumo,
  FinanceiroEvolucaoSalarialResponse,
  FinanceiroBatchStatusResponse,
  FinanceiroBatchUploadResponse,
} from "./financeiro.model"

export async function analisarContracheque(
  payload: FormData,
): Promise<ContrachequeAnalise> {
  const response = await apiFetch("/api/financeiro/contracheque/analisar", {
    method: "POST",
    body: payload,
  })

  return parseApiResponse<ContrachequeAnalise>(
    response,
    "We could not analyze the pay stub.",
  )
}

export async function enviarLoteContracheques(
  payload: FormData,
): Promise<FinanceiroBatchUploadResponse> {
  const response = await apiFetch("/api/financeiro/upload-lote", {
    method: "POST",
    body: payload,
  })

  return parseApiResponse<FinanceiroBatchUploadResponse>(
    response,
    "We could not start the pay stub batch.",
  )
}

export async function obterStatusLoteFinanceiro(
  batchId: number,
): Promise<FinanceiroBatchStatusResponse> {
  const response = await apiFetch(`/api/financeiro/batch/${batchId}`, {
    method: "GET",
  })

  return parseApiResponse<FinanceiroBatchStatusResponse>(
    response,
    "We could not fetch the batch status.",
  )
}

export async function obterEvolucaoSalarialPersistida(
  userId: number,
): Promise<FinanceiroEvolucaoSalarialResponse> {
  const response = await apiFetch(`/api/financeiro/evolucao-salarial?user_id=${userId}`, {
    method: "GET",
  })

  return parseApiResponse<FinanceiroEvolucaoSalarialResponse>(
    response,
    "We could not load the persisted salary analysis.",
  )
}

export async function obterContrachequesSalvos(
  userId: number,
): Promise<FinanceiroContrachequeResumo[]> {
  const response = await apiFetch(`/api/financeiro/contracheques?user_id=${userId}`, {
    method: "GET",
  })

  return parseApiResponse<FinanceiroContrachequeResumo[]>(
    response,
    "We could not load the saved pay stubs.",
  )
}

export async function obterEvolucaoSalarialLote(
  batchId: number,
): Promise<FinanceiroEvolucaoSalarialResponse> {
  const response = await apiFetch(`/api/financeiro/batch/${batchId}/evolucao-salarial`, {
    method: "GET",
  })

  return parseApiResponse<FinanceiroEvolucaoSalarialResponse>(
    response,
    "We could not fetch the salary evolution.",
  )
}
