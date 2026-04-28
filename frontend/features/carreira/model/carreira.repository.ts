import type { CadastroCarreira, ResumoCarreira } from "./carreira.model"
import { apiFetch, parseApiResponse } from "@/shared/api/client"

export async function buscarResumoCarreira(
  cadastro: CadastroCarreira,
): Promise<ResumoCarreira> {
  const response = await apiFetch("/api/carreira/resumo", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(cadastro),
  })

  return parseApiResponse<ResumoCarreira>(response, "Erro ao calcular")
}
