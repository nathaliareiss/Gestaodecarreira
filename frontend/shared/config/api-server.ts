const API_URL_LOCAL_PADRAO = "http://localhost:8000"

export function obterApiBaseUrlServidor() {
  const urlConfigurada = process.env.NEXT_PUBLIC_API_URL?.trim()
  const urlBase = urlConfigurada ?? API_URL_LOCAL_PADRAO

  if (urlBase.startsWith("http://") || urlBase.startsWith("https://")) {
    return urlBase.replace(/\/$/, "")
  }

  return `http://${urlBase.replace(/\/$/, "")}`
}
