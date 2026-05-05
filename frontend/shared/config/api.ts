export function obterApiBaseUrl() {
  const urlConfigurada = process.env.NEXT_PUBLIC_API_URL?.trim()
  if (!urlConfigurada) {
    throw new Error("NEXT_PUBLIC_API_URL nao foi definido.")
  }

  if (urlConfigurada.startsWith("http://") || urlConfigurada.startsWith("https://")) {
    return urlConfigurada.replace(/\/$/, "")
  }

  return `http://${urlConfigurada.replace(/\/$/, "")}`
}
