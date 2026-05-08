function criarAbortError() {
  const erro = new Error("Polling aborted.")
  erro.name = "AbortError"
  return erro
}

export function isBatchTerminalStatus(status) {
  return status === "completed" || status === "failed"
}

export function calcularProgressoLote(status) {
  const total = Number(status?.total ?? 0)
  if (!Number.isFinite(total) || total <= 0) {
    return 0
  }

  const processed = Math.max(0, Number(status?.processed_count ?? status?.processed ?? 0))
  const duplicated = Math.max(0, Number(status?.duplicated_count ?? status?.duplicated ?? 0))
  const failed = Math.max(0, Number(status?.failed_count ?? status?.failed ?? 0))
  const completo = Math.min(total, processed + duplicated + failed)

  return Math.min(100, Math.round((completo / total) * 100))
}

export function formatarStatusLote(status) {
  switch (status) {
    case "pending":
      return "Pending"
    case "processing":
      return "Processing"
    case "completed":
      return "Completed"
    case "failed":
      return "Failed"
    default:
      return "Unknown"
  }
}

function esperar(ms, signal) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(criarAbortError())
      return
    }

    const timeoutId = setTimeout(() => {
      limpar()
      resolve()
    }, ms)

    function aoCancelar() {
      clearTimeout(timeoutId)
      limpar()
      reject(criarAbortError())
    }

    function limpar() {
      signal?.removeEventListener("abort", aoCancelar)
    }

    signal?.addEventListener("abort", aoCancelar, { once: true })
  })
}

export async function acompanharLoteFinanceiro({
  batchId,
  fetchStatus,
  delayMs = 2000,
  signal,
  onUpdate,
  wait = esperar,
}) {
  let statusAtual = await fetchStatus(batchId)
  onUpdate?.(statusAtual)

  while (!isBatchTerminalStatus(statusAtual.status)) {
    if (typeof wait === "function") {
      await wait(delayMs, signal)
    } else {
      await esperar(delayMs, signal)
    }
    if (signal?.aborted) {
      throw criarAbortError()
    }

    statusAtual = await fetchStatus(batchId)
    onUpdate?.(statusAtual)
  }

  return statusAtual
}
