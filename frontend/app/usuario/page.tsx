import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import type { UsuarioConta } from "@/features/usuario/model/usuario.model"
import { UsuarioPageController } from "@/features/usuario/controller/usuario-page-controller"
import type { HistoricoFuncionalAnalise } from "@/features/historico-funcional/model/historico-funcional.model"
import { AUTH_COOKIE_NAME, AUTH_USER_COOKIE_NAME } from "@/shared/auth/session"
import { obterApiBaseUrlServidor } from "@/shared/config/api-server"
import { parseApiResponse } from "@/shared/api/client"

export const dynamic = "force-dynamic"

async function carregarHistoricoInicial(
  usuarioId: number,
): Promise<HistoricoFuncionalAnalise | null> {
  try {
    const response = await fetch(
      `${obterApiBaseUrlServidor()}/api/historicos-funcionais/usuario/${usuarioId}/ultimo`,
      {
        cache: "no-store",
      },
    )

    if (response.status === 404) {
      return null
    }

    return parseApiResponse<HistoricoFuncionalAnalise>(
      response,
      "Erro ao carregar o histórico funcional.",
    )
  } catch {
    return null
  }
}

async function carregarUsuarioAutenticadoInicial(token: string): Promise<UsuarioConta | null> {
  try {
    const response = await fetch(`${obterApiBaseUrlServidor()}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    })

    if (!response.ok) {
      redirect("/login")
    }

    return await parseApiResponse<UsuarioConta>(response, "Não foi possível carregar a sessão.")
  } catch {
    redirect("/login")
  }
}

function safeParseUsuarioCache(valor: string): UsuarioConta | null {
  try {
    return JSON.parse(decodeURIComponent(valor)) as UsuarioConta
  } catch {
    return null
  }
}

export default async function UsuarioPage() {
  const cookieStore = await cookies()
  const token = cookieStore.get(AUTH_COOKIE_NAME)?.value
  if (!token) {
    redirect("/login")
  }

  const usuarioCacheRaw = cookieStore.get(AUTH_USER_COOKIE_NAME)?.value
  const usuarioCache = usuarioCacheRaw ? safeParseUsuarioCache(usuarioCacheRaw) : null

  const usuarioPromise = carregarUsuarioAutenticadoInicial(token)
  const historicoPromise = usuarioCache ? carregarHistoricoInicial(usuarioCache.id) : null

  const usuario = await usuarioPromise

  if (!usuario) {
    redirect("/login")
  }

  const historicoInicial = historicoPromise
    ? await historicoPromise
    : await carregarHistoricoInicial(usuario.id)

  return (
    <UsuarioPageController
      usuarioInicial={usuario}
      historicoInicial={historicoInicial}
      erroInicial={null}
    />
  )
}
