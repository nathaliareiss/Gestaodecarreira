export function obterApiBaseUrl() {
  const url = process.env.NEXT_PUBLIC_API_URL ?? "https://astonishing-forgiveness-production-c90d.up.railway.app"
  return url.startsWith("http://") || url.startsWith("https://") ? url.replace(/\/$/, "") : `https://${url.replace(/\/$/, "")}`
}
