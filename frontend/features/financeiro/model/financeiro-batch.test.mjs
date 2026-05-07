import assert from "node:assert/strict"

import {
  acompanharLoteFinanceiro,
  calcularProgressoLote,
  formatarStatusLote,
  isBatchTerminalStatus,
} from "./financeiro-batch.mjs"

async function executar() {
  assert.equal(
    calcularProgressoLote({
      total: 5,
      processed: 3,
      failed: 1,
      status: "processing",
    }),
    80,
  )

  assert.equal(isBatchTerminalStatus("completed"), true)
  assert.equal(isBatchTerminalStatus("failed"), true)
  assert.equal(isBatchTerminalStatus("processing"), false)

  assert.equal(formatarStatusLote("pending"), "Pending")
  assert.equal(formatarStatusLote("completed"), "Completed")

  const statuses = [
    { total: 5, processed: 1, failed: 0, status: "processing" },
    { total: 5, processed: 3, failed: 1, status: "processing" },
    { total: 5, processed: 4, failed: 1, status: "completed" },
  ]
  const chamadas = []
  let esperas = 0

  const final = await acompanharLoteFinanceiro({
    batchId: 42,
    fetchStatus: async (batchId) => {
      chamadas.push(batchId)
      return statuses.shift()
    },
    wait: async () => {
      esperas += 1
    },
  })

  assert.equal(final.status, "completed")
  assert.equal(chamadas.length, 3)
  assert.equal(esperas, 2)
}

executar()
  .then(() => {
    console.log("financeiro-batch polling tests passed")
  })
  .catch((error) => {
    console.error(error)
    process.exitCode = 1
  })
