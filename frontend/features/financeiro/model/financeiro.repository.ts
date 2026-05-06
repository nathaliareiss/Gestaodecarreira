import { apiFetch, parseApiResponse } from "@/shared/api/client"

import type { ContrachequeAnalise } from "./financeiro.model"

export async function analisarContracheque(
  payload: FormData,
): Promise<ContrachequeAnalise> {
  const response = await apiFetch("/api/financeiro/contracheque/analisar", {
    method: "POST",
    body: payload,
  })

  return parseApiResponse<ContrachequeAnalise>(
    response,
    "Nao foi possivel analisar o contracheque.",
  )
}
