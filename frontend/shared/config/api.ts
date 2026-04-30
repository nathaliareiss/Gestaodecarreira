const API_URL_LOCAL_PADRAO = "http://localhost:8000"
const API_URL_PRODUCAO_PADRAO = "https://astonishing-forgiveness-production-c90d.up.railway.app"

export function obterApiBaseUrl() {
  const urlConfigurada = process.env.NEXT_PUBLIC_API_URL?.trim()
  const urlBase =
    urlConfigurada ?? (process.env.NODE_ENV === "production" ? API_URL_PRODUCAO_PADRAO : API_URL_LOCAL_PADRAO)

  if (urlBase.startsWith("http://") || urlBase.startsWith("https://")) {
    return urlBase.replace(/\/$/, "")
  }

  return `${process.env.NODE_ENV === "production" ? "https://" : "http://"}${urlBase.replace(/\/$/, "")}`
}
