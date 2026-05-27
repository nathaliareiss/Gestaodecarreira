import type {
  UsuarioAuthResponse,
  UsuarioLogin,
  UsuarioReenviarConfirmacaoEmail,
  UsuarioSolicitacaoRecuperacaoSenha,
  UsuarioRedefinicaoSenha,
} from "./auth.model"
import type { UsuarioConta } from "@/features/usuario/model/usuario.model"
import { apiFetch, parseApiResponse } from "@/shared/api/client"

export async function autenticarUsuario(
  dadosLogin: UsuarioLogin,
): Promise<UsuarioAuthResponse> {
  const response = await apiFetch("/api/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(dadosLogin),
  })

  return parseApiResponse<UsuarioAuthResponse>(response, "Não foi possível entrar.")
}

export async function carregarUsuarioAutenticado(): Promise<UsuarioConta> {
  const response = await apiFetch("/api/auth/me", {
    method: "GET",
    cache: "no-store",
  })

  return parseApiResponse<UsuarioConta>(response, "Não foi possível carregar a sessão.")
}

export async function encerrarSessao(): Promise<void> {
  const response = await apiFetch("/api/auth/logout", {
    method: "POST",
  })

  await parseApiResponse<{ status: string }>(response, "Não foi possível sair.")
}

export async function solicitarRecuperacaoSenha(
  dados: UsuarioSolicitacaoRecuperacaoSenha,
): Promise<{ status: string; message: string }> {
  const response = await apiFetch("/api/auth/solicitar-recuperacao-senha", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(dados),
  })

  return parseApiResponse<{ status: string; message: string }>(
    response,
    "Não foi possível solicitar a recuperação de senha.",
  )
}

export async function confirmarEmailUsuario(token: string): Promise<UsuarioAuthResponse> {
  const response = await apiFetch("/api/auth/confirmar-email", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ token }),
  })

  return parseApiResponse<UsuarioAuthResponse>(
    response,
    "Nao foi possivel confirmar o e-mail.",
  )
}

export async function reenviarConfirmacaoEmail(
  dados: UsuarioReenviarConfirmacaoEmail,
): Promise<{ status: string; message: string }> {
  const response = await apiFetch("/api/auth/reenviar-confirmacao-email", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(dados),
  })

  return parseApiResponse<{ status: string; message: string }>(
    response,
    "Não foi possível reenviar o e-mail de confirmação.",
  )
}

export async function redefinirSenhaUsuario(
  dados: UsuarioRedefinicaoSenha,
): Promise<{ status: string; message: string }> {
  const response = await apiFetch("/api/auth/redefinir-senha", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(dados),
  })

  return parseApiResponse<{ status: string; message: string }>(
    response,
    "Não foi possível redefinir a senha.",
  )
}
