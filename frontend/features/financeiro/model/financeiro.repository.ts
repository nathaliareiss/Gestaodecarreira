import { apiFetch, parseApiResponse } from "@/shared/api/client"

import type {
  ContrachequeAnalise,
  FinanceiroContrachequeResumo,
  FinanceiroEvolucaoSalarialResponse,
  FinanceiroBatchStatusResponse,
  FinanceiroBatchUploadResponse,
  FinanceiroImportacaoTemporariaCriacaoResponse,
  FinanceiroImportacaoTemporariaValidacaoRequest,
  FinanceiroImportacaoTemporariaValidacaoResponse,
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

export async function criarImportacaoTemporariaFinanceiro(): Promise<FinanceiroImportacaoTemporariaCriacaoResponse> {
  const response = await apiFetch("/api/financeiro/importacao-temporaria", {
    method: "POST",
  })

  return parseApiResponse<FinanceiroImportacaoTemporariaCriacaoResponse>(
    response,
    "We could not create the temporary import token.",
  )
}

export async function validarImportacaoTemporariaFinanceiro(
  token: string,
): Promise<FinanceiroImportacaoTemporariaValidacaoResponse> {
  const payload: FinanceiroImportacaoTemporariaValidacaoRequest = { token }
  const response = await apiFetch("/api/financeiro/importacao-temporaria/validar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  return parseApiResponse<FinanceiroImportacaoTemporariaValidacaoResponse>(
    response,
    "We could not validate the temporary import token.",
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

export async function obterEvolucaoSalarialPersistida(): Promise<FinanceiroEvolucaoSalarialResponse> {
  const response = await apiFetch("/api/financeiro/evolucao-salarial", {
    method: "GET",
  })

  return parseApiResponse<FinanceiroEvolucaoSalarialResponse>(
    response,
    "We could not load the persisted salary analysis.",
  )
}

export async function obterContrachequesSalvos(): Promise<FinanceiroContrachequeResumo[]> {
  const response = await apiFetch("/api/financeiro/contracheques", {
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
