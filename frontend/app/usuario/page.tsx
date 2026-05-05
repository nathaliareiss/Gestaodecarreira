import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import type { UsuarioConta } from "@/features/usuario/model/usuario.model"
import { UsuarioPageController } from "@/features/usuario/controller/usuario-page-controller"
import type { HistoricoFuncionalAnalise } from "@/features/historico-funcional/model/historico-funcional.model"
import { AUTH_COOKIE_NAME } from "@/shared/auth/session"
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

async function carregarUsuarioAutenticadoInicial(): Promise<UsuarioConta | null> {
  const cookieStore = await cookies()
  const token = cookieStore.get(AUTH_COOKIE_NAME)?.value
  if (!token) {
    redirect("/login")
  }

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

export default async function UsuarioPage() {
  const usuario = await carregarUsuarioAutenticadoInicial()

  if (!usuario) {
    redirect("/login")
  }

  const historicoInicial = await carregarHistoricoInicial(usuario.id)

  return (
    <UsuarioPageController
      usuarioInicial={usuario}
      historicoInicial={historicoInicial}
      erroInicial={null}
    />
  )
}

