import { obterApiBaseUrl } from "@/shared/config/api"

import type { UsuarioCadastro, UsuarioConta } from "./usuario.model"

type RespostaErroApi = {
  detail?: string
}

async function lerResposta<T>(response: Response, mensagemPadrao: string): Promise<T> {
  const dados = (await response.json().catch(() => null)) as T | RespostaErroApi | null

  if (!response.ok) {
    const mensagem =
      dados && typeof dados === "object" && "detail" in dados
        ? dados.detail ?? mensagemPadrao
        : mensagemPadrao
    throw new Error(mensagem)
  }

  return dados as T
}

export async function criarUsuario(
  cadastro: UsuarioCadastro,
): Promise<UsuarioConta> {
  const response = await fetch(`${obterApiBaseUrl()}/api/usuarios`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(cadastro),
  })

  return lerResposta<UsuarioConta>(response, "Erro ao cadastrar usuario")
}

export async function listarUsuarios(): Promise<UsuarioConta[]> {
  const response = await fetch(`${obterApiBaseUrl()}/api/usuarios`, {
    method: "GET",
  })

  return lerResposta<UsuarioConta[]>(response, "Erro ao carregar usuarios")
}

export async function buscarUsuarioMaisRecente(): Promise<UsuarioConta | null> {
  const response = await fetch(`${obterApiBaseUrl()}/api/usuarios/ultimo`, {
    method: "GET",
  })

  if (response.status === 404) {
    return null
  }

  return lerResposta<UsuarioConta>(response, "Erro ao carregar usuario")
}

export async function confirmarUsuarioPorToken(
  token: string,
): Promise<UsuarioConta> {
  const response = await fetch(`${obterApiBaseUrl()}/api/usuarios/confirmar`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ token }),
  })

  return lerResposta<UsuarioConta>(response, "Nao foi possivel confirmar o email")
}

export async function removerUsuarioMaisRecente(): Promise<void> {
  const response = await fetch(`${obterApiBaseUrl()}/api/usuarios/ultimo`, {
    method: "DELETE",
  })

  await lerResposta<{ status: string }>(response, "Nao foi possivel remover o usuario")
}
