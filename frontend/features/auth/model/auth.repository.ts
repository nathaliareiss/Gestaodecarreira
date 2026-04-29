import type {
  UsuarioAuthResponse,
  UsuarioLogin,
  UsuarioRecuperacaoSenha,
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

  return parseApiResponse<UsuarioAuthResponse>(response, "Nao foi possivel entrar")
}

export async function carregarUsuarioAutenticado(token: string): Promise<UsuarioConta> {
  const response = await apiFetch("/api/auth/me", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  })

  return parseApiResponse<UsuarioConta>(response, "Nao foi possivel carregar a sessao")
}

export async function encerrarSessao(token: string): Promise<void> {
  const response = await apiFetch("/api/auth/logout", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  await parseApiResponse<{ status: string }>(response, "Nao foi possivel sair")
}

export async function redefinirSenhaUsuario(
  dados: UsuarioRecuperacaoSenha,
): Promise<{ status: string; message: string }> {
  const response = await apiFetch("/api/auth/recuperar-senha", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(dados),
  })

  return parseApiResponse<{ status: string; message: string }>(
    response,
    "Nao foi possivel recuperar a senha",
  )
}

