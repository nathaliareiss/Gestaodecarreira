import type { UsuarioConta } from "@/features/usuario/model/usuario.model"

export const AUTH_COOKIE_NAME = "gc_auth_token"
export const AUTH_USER_COOKIE_NAME = "gc_auth_user"
export const DEMO_MODE_COOKIE_NAME = "gc_demo_mode"
export const DEMO_SESSION_TOKEN = "demo-session"
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

function getUsuarioCookiePair(valor: string) {
  return `${AUTH_USER_COOKIE_NAME}=${encodeURIComponent(valor)}`
}

export function salvarUsuarioAutenticadoCache(usuario: UsuarioConta) {
  document.cookie = [
    getUsuarioCookiePair(JSON.stringify(usuario)),
    "Path=/",
    `Max-Age=${AUTH_COOKIE_MAX_AGE}`,
    "SameSite=Lax",
  ].join("; ")
}

export function removerUsuarioAutenticadoCache() {
  document.cookie = [getUsuarioCookiePair(""), "Path=/", "Max-Age=0", "SameSite=Lax"].join("; ")
}

function getDemoModeCookiePair(valor: string) {
  return `${DEMO_MODE_COOKIE_NAME}=${encodeURIComponent(valor)}`
}

export function salvarSessaoDemo(usuario: UsuarioConta) {
  salvarTokenAutenticacao(DEMO_SESSION_TOKEN)
  salvarUsuarioAutenticadoCache(usuario)
  document.cookie = [getDemoModeCookiePair("1"), "Path=/", `Max-Age=${AUTH_COOKIE_MAX_AGE}`, "SameSite=Lax"].join(
    "; ",
  )

  if (typeof window !== "undefined") {
    window.localStorage.setItem(DEMO_MODE_COOKIE_NAME, "1")
  }
}

export function removerSessaoDemo() {
  removerTokenAutenticacao()
  removerUsuarioAutenticadoCache()
  document.cookie = [getDemoModeCookiePair(""), "Path=/", "Max-Age=0", "SameSite=Lax"].join("; ")

  if (typeof window !== "undefined") {
    window.localStorage.removeItem(DEMO_MODE_COOKIE_NAME)
  }
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

export function obterUsuarioAutenticadoCache(): UsuarioConta | null {
  const cookies = document.cookie
    .split(";")
    .map((item) => item.trim())
    .filter(Boolean)

  const entrada = cookies.find((item) => item.startsWith(`${AUTH_USER_COOKIE_NAME}=`))
  if (!entrada) {
    return null
  }

  try {
    return JSON.parse(decodeURIComponent(entrada.slice(AUTH_USER_COOKIE_NAME.length + 1))) as UsuarioConta
  } catch {
    return null
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

