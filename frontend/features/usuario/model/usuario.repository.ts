import type { UsuarioCadastro, UsuarioConta } from "./usuario.model"
import { apiFetch, parseApiResponse } from "@/shared/api/client"

export async function criarUsuario(
  cadastro: UsuarioCadastro,
): Promise<UsuarioConta> {
  const response = await apiFetch("/api/usuarios", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(cadastro),
  })

  return parseApiResponse<UsuarioConta>(response, "Erro ao cadastrar usuario")
}

export async function listarUsuarios(): Promise<UsuarioConta[]> {
  const response = await apiFetch("/api/usuarios", {
    method: "GET",
  })

  return parseApiResponse<UsuarioConta[]>(response, "Erro ao carregar usuarios")
}

export async function buscarUsuarioMaisRecente(): Promise<UsuarioConta | null> {
  const response = await apiFetch("/api/usuarios/ultimo", {
    method: "GET",
  })

  if (response.status === 404) {
    return null
  }

  return parseApiResponse<UsuarioConta>(response, "Erro ao carregar usuario")
}

export async function confirmarUsuarioPorToken(
  token: string,
): Promise<UsuarioConta> {
  const response = await apiFetch("/api/usuarios/confirmar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ token }),
  })

  return parseApiResponse<UsuarioConta>(response, "Nao foi possivel confirmar o email")
}

export async function removerUsuarioMaisRecente(): Promise<void> {
  const response = await apiFetch("/api/usuarios/ultimo", {
    method: "DELETE",
  })

  await parseApiResponse<{ status: string }>(response, "Nao foi possivel remover o usuario")
}
