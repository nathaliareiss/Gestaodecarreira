import { apiFetch, parseApiResponse } from "@/shared/api/client"

import type {
  ContrachequeAnalise,
  FinanceiroContrachequeResumo,
  FinanceiroEvolucaoSalarialResponse,
  FinanceiroEvolucaoSalarialSerieItem,
  FinanceiroBatchStatusResponse,
  FinanceiroBatchUploadResponse,
  FinanceiroImportacaoTemporariaCriacaoResponse,
  FinanceiroImportacaoTemporariaValidacaoRequest,
  FinanceiroImportacaoTemporariaValidacaoResponse,
} from "./financeiro.model"

function listaDeStringsSegura(valor: unknown): string[] {
  if (!Array.isArray(valor)) {
    return []
  }

  return valor
    .map((item) => String(item ?? "").trim())
    .filter((item) => item.length > 0)
}

function listaDeNumerosSegura(valor: unknown): number[] {
  if (!Array.isArray(valor)) {
    return []
  }

  return valor
    .map((item) => Number(item))
    .filter((item) => Number.isFinite(item))
}

function numeroSeguro(valor: unknown, padrao = 0): number {
  const numero = typeof valor === "number" ? valor : Number(valor)
  return Number.isFinite(numero) ? numero : padrao
}

function mapaNumeroSeguro(valor: unknown): Record<string, number> {
  if (!valor || typeof valor !== "object" || Array.isArray(valor)) {
    return {}
  }

  return Object.fromEntries(
    Object.entries(valor as Record<string, unknown>).map(([chave, item]) => [chave, numeroSeguro(item)]),
  )
}

function normalizarStatusLote(
  resposta: Partial<FinanceiroBatchStatusResponse> | null | undefined,
): FinanceiroBatchStatusResponse {
  return {
    total: numeroSeguro(resposta?.total),
    processed_count: numeroSeguro(resposta?.processed_count ?? resposta?.processed),
    duplicated_count: numeroSeguro(resposta?.duplicated_count ?? resposta?.duplicated),
    failed_count: numeroSeguro(resposta?.failed_count ?? resposta?.failed),
    status: resposta?.status ?? "pending",
    last_error_message:
      typeof resposta?.last_error_message === "string" && resposta.last_error_message.trim().length > 0
        ? resposta.last_error_message
        : null,
    failure_messages: listaDeStringsSegura(resposta?.failure_messages),
    processed: numeroSeguro(resposta?.processed),
    duplicated: numeroSeguro(resposta?.duplicated),
    failed: numeroSeguro(resposta?.failed),
  }
}

function normalizarUploadLote(
  resposta: Partial<FinanceiroBatchUploadResponse> | null | undefined,
): FinanceiroBatchUploadResponse {
  return {
    batch_id: numeroSeguro(resposta?.batch_id),
    status: resposta?.status ?? "pending",
  }
}

function normalizarImportacaoCriada(
  resposta: Partial<FinanceiroImportacaoTemporariaCriacaoResponse> | null | undefined,
): FinanceiroImportacaoTemporariaCriacaoResponse {
  return {
    token: typeof resposta?.token === "string" ? resposta.token : "",
    expires_at: typeof resposta?.expires_at === "string" ? resposta.expires_at : new Date(0).toISOString(),
    scope: typeof resposta?.scope === "string" ? resposta.scope : "financeiro_importacao",
  }
}

function normalizarImportacaoValidada(
  resposta: Partial<FinanceiroImportacaoTemporariaValidacaoResponse> | null | undefined,
): FinanceiroImportacaoTemporariaValidacaoResponse {
  return {
    valid: Boolean(resposta?.valid),
    scope: typeof resposta?.scope === "string" ? resposta.scope : "financeiro_importacao",
    user_id: numeroSeguro(resposta?.user_id),
    expires_at: typeof resposta?.expires_at === "string" ? resposta.expires_at : new Date(0).toISOString(),
    used: Boolean(resposta?.used),
  }
}

function normalizarSerieEvolucao(
  serie: Partial<FinanceiroEvolucaoSalarialSerieItem> | null | undefined,
): FinanceiroEvolucaoSalarialSerieItem {
  return {
    ano: numeroSeguro(serie?.ano),
    salario_base_referencia_anual: numeroSeguro(serie?.salario_base_referencia_anual),
    bruto_total_referencia_anual: numeroSeguro(serie?.bruto_total_referencia_anual),
    liquido_referencia_anual: numeroSeguro(serie?.liquido_referencia_anual),
    descontos_referencia_anual: numeroSeguro(serie?.descontos_referencia_anual),
    vantagens_adicionais_referencia_anual: numeroSeguro(serie?.vantagens_adicionais_referencia_anual),
    composicao_vantagens_referencia_anual: mapaNumeroSeguro(serie?.composicao_vantagens_referencia_anual),
    composicao_descontos_referencia_anual: mapaNumeroSeguro(serie?.composicao_descontos_referencia_anual),
    quantidade_contracheques: numeroSeguro(serie?.quantidade_contracheques),
    variacao_percentual_salario_base_ano_a_ano:
      typeof serie?.variacao_percentual_salario_base_ano_a_ano === "number"
        ? serie.variacao_percentual_salario_base_ano_a_ano
        : null,
    crescimento_relevante: Boolean(serie?.crescimento_relevante),
  }
}

function normalizarEvolucaoSalarial(
  resposta: Partial<FinanceiroEvolucaoSalarialResponse> | null | undefined,
): FinanceiroEvolucaoSalarialResponse {
  return {
    batch_id: resposta?.batch_id ?? null,
    ano_inicial: resposta?.ano_inicial ?? null,
    ano_final: resposta?.ano_final ?? null,
    salario_base_inicial_referencia: resposta?.salario_base_inicial_referencia ?? null,
    salario_base_final_referencia: resposta?.salario_base_final_referencia ?? null,
    bruto_total_inicial_referencia: resposta?.bruto_total_inicial_referencia ?? null,
    bruto_total_final_referencia: resposta?.bruto_total_final_referencia ?? null,
    liquido_inicial_referencia: resposta?.liquido_inicial_referencia ?? null,
    liquido_final_referencia: resposta?.liquido_final_referencia ?? null,
    descontos_inicial_referencia: resposta?.descontos_inicial_referencia ?? null,
    descontos_final_referencia: resposta?.descontos_final_referencia ?? null,
    vantagens_adicionais_inicial_referencia: resposta?.vantagens_adicionais_inicial_referencia ?? null,
    vantagens_adicionais_final_referencia: resposta?.vantagens_adicionais_final_referencia ?? null,
    variacao_acumulada_salario_base_percentual:
      resposta?.variacao_acumulada_salario_base_percentual ?? null,
    anos_sem_crescimento_relevante: listaDeNumerosSegura(resposta?.anos_sem_crescimento_relevante),
    series: Array.isArray(resposta?.series)
      ? resposta.series.map((serie) => normalizarSerieEvolucao(serie))
      : [],
  }
}

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

  const dados = await parseApiResponse<Partial<FinanceiroBatchUploadResponse> | null>(
    response,
    "We could not start the pay stub batch.",
  )

  return normalizarUploadLote(dados)
}

export async function criarImportacaoTemporariaFinanceiro(): Promise<FinanceiroImportacaoTemporariaCriacaoResponse> {
  const response = await apiFetch("/api/financeiro/importacao-temporaria", {
    method: "POST",
  })

  const dados = await parseApiResponse<Partial<FinanceiroImportacaoTemporariaCriacaoResponse> | null>(
    response,
    "We could not create the temporary import token.",
  )

  return normalizarImportacaoCriada(dados)
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

  const dados = await parseApiResponse<Partial<FinanceiroImportacaoTemporariaValidacaoResponse> | null>(
    response,
    "We could not validate the temporary import token.",
  )

  return normalizarImportacaoValidada(dados)
}

export async function obterStatusLoteFinanceiro(
  batchId: number,
): Promise<FinanceiroBatchStatusResponse> {
  const response = await apiFetch(`/api/financeiro/batch/${batchId}`, {
    method: "GET",
  })

  const dados = await parseApiResponse<Partial<FinanceiroBatchStatusResponse> | null>(
    response,
    "We could not fetch the batch status.",
  )

  return normalizarStatusLote(dados)
}

export async function obterEvolucaoSalarialPersistida(): Promise<FinanceiroEvolucaoSalarialResponse> {
  const response = await apiFetch("/api/financeiro/evolucao-salarial", {
    method: "GET",
  })

  const dados = await parseApiResponse<Partial<FinanceiroEvolucaoSalarialResponse> | null>(
    response,
    "We could not load the persisted salary analysis.",
  )

  return normalizarEvolucaoSalarial(dados)
}

export async function obterContrachequesSalvos(): Promise<FinanceiroContrachequeResumo[]> {
  const response = await apiFetch("/api/financeiro/contracheques", {
    method: "GET",
  })

  const dados = await parseApiResponse<FinanceiroContrachequeResumo[] | null>(
    response,
    "We could not load the saved pay stubs.",
  )

  return Array.isArray(dados) ? dados : []
}

export async function obterEvolucaoSalarialLote(
  batchId: number,
): Promise<FinanceiroEvolucaoSalarialResponse> {
  const response = await apiFetch(`/api/financeiro/batch/${batchId}/evolucao-salarial`, {
    method: "GET",
  })

  const dados = await parseApiResponse<Partial<FinanceiroEvolucaoSalarialResponse> | null>(
    response,
    "We could not fetch the salary evolution.",
  )

  return normalizarEvolucaoSalarial(dados)
}
