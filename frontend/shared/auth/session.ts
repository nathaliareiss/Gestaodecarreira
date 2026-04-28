export const AUTH_COOKIE_NAME = "gc_auth_token"
const AUTH_COOKIE_MAX_AGE = 60 * 60 * 24 * 7

function getCookiePair(valor: string) {
  return `${AUTH_COOKIE_NAME}=${encodeURIComponent(valor)}`
}

export function salvarTokenAutenticacao(token: string) {
  document.cookie = [
    getCookiePair(token),
    "Path=/",
    `Max-Age=${AUTH_COOKIE_MAX_AGE}`,
    "SameSite=Lax",
  ].join("; ")
}

export function removerTokenAutenticacao() {
  document.cookie = [getCookiePair(""), "Path=/", "Max-Age=0", "SameSite=Lax"].join("; ")
}

export function obterTokenAutenticacao(): string | null {
  const cookies = document.cookie
    .split(";")
    .map((item) => item.trim())
    .filter(Boolean)

  const entrada = cookies.find((item) => item.startsWith(`${AUTH_COOKIE_NAME}=`))
  if (!entrada) {
    return null
  }

  return decodeURIComponent(entrada.slice(AUTH_COOKIE_NAME.length + 1))
}

