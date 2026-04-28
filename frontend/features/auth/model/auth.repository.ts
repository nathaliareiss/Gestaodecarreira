import { obterApiBaseUrl } from "@/shared/config/api"

import type { UsuarioAuthResponse, UsuarioLogin } from "./auth.model"
import type { UsuarioConta } from "@/features/usuario/model/usuario.model"

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

export async function autenticarUsuario(
  dadosLogin: UsuarioLogin,
): Promise<UsuarioAuthResponse> {
  const response = await fetch(`${obterApiBaseUrl()}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(dadosLogin),
  })

  return lerResposta<UsuarioAuthResponse>(response, "Nao foi possivel entrar")
}

export async function carregarUsuarioAutenticado(token: string): Promise<UsuarioConta> {
  const response = await fetch(`${obterApiBaseUrl()}/api/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: "no-store",
  })

  return lerResposta<UsuarioConta>(response, "Nao foi possivel carregar a sessao")
}

export async function encerrarSessao(token: string): Promise<void> {
  const response = await fetch(`${obterApiBaseUrl()}/api/auth/logout`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  await lerResposta<{ status: string }>(response, "Nao foi possivel sair")
}

