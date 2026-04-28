import { USUARIO_STORAGE_KEY, type UsuarioConta } from "./usuario.model"

function lerStorage(): UsuarioConta | null {
  if (typeof window === "undefined") {
    return null
  }

  const valor = window.localStorage.getItem(USUARIO_STORAGE_KEY)
  if (!valor) {
    return null
  }

  try {
    return JSON.parse(valor) as UsuarioConta
  } catch {
    return null
  }
}

export function carregarUsuario(): UsuarioConta | null {
  return lerStorage()
}

export function salvarUsuario(usuario: UsuarioConta) {
  window.localStorage.setItem(USUARIO_STORAGE_KEY, JSON.stringify(usuario))
}

export function limparUsuario() {
  window.localStorage.removeItem(USUARIO_STORAGE_KEY)
}

export function gerarLinkConfirmacao(token: string) {
  return `/confirmar-email?token=${encodeURIComponent(token)}`
}

export function confirmarUsuarioPorToken(token: string) {
  const usuario = lerStorage()

  if (!usuario || usuario.token_confirmacao_email !== token) {
    return null
  }

  if (!usuario.email_confirmado) {
    usuario.email_confirmado = true
    usuario.confirmado_em = new Date().toISOString()
    salvarUsuario(usuario)
  }

  return usuario
}
