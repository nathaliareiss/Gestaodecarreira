export const AUTH_USER_COOKIE_NAME = "gc_auth_user"
export const AUTH_TOKEN_COOKIE_NAME = "gc_auth_token"
export const DEMO_MODE_COOKIE_NAME = "gc_demo_mode"
const AUTH_COOKIE_MAX_AGE = 60 * 60 * 24 * 7

function getCookiePair(nome: string, valor: string) {
  return `${nome}=${encodeURIComponent(valor)}`
}

export function removerUsuarioAutenticadoId() {
  document.cookie = [getCookiePair(AUTH_USER_COOKIE_NAME, ""), "Path=/", "Max-Age=0", "SameSite=Lax"].join("; ")
}

function getDemoModeCookiePair(valor: string) {
  return `${DEMO_MODE_COOKIE_NAME}=${encodeURIComponent(valor)}`
}

export function salvarSessaoDemo() {
  document.cookie = [getDemoModeCookiePair("1"), "Path=/", `Max-Age=${AUTH_COOKIE_MAX_AGE}`, "SameSite=Lax"].join(
    "; ",
  )

  if (typeof window !== "undefined") {
    window.localStorage.setItem(DEMO_MODE_COOKIE_NAME, "1")
  }
}

export function removerSessaoDemo() {
  removerUsuarioAutenticadoId()
  document.cookie = [getDemoModeCookiePair(""), "Path=/", "Max-Age=0", "SameSite=Lax"].join("; ")

  if (typeof window !== "undefined") {
    window.localStorage.removeItem(DEMO_MODE_COOKIE_NAME)
  }
}

export function modoDemoAtivoNoCliente(): boolean {
  const demoAtivoNoCookie = document.cookie
    .split(";")
    .map((item) => item.trim())
    .filter(Boolean)
    .some((item) => item.startsWith(`${DEMO_MODE_COOKIE_NAME}=`))

  if (demoAtivoNoCookie) {
    return true
  }

  try {
    return window.localStorage.getItem(DEMO_MODE_COOKIE_NAME) === "1"
  } catch {
    return false
  }
}
