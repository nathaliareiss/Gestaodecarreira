import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import type { UsuarioConta } from "@/features/usuario/model/usuario.model"
import { UsuarioPageController } from "@/features/usuario/controller/usuario-page-controller"
import type { HistoricoFuncionalAnalise } from "@/features/historico-funcional/model/historico-funcional.model"
import { AUTH_COOKIE_NAME } from "@/shared/auth/session"
import { carregarUsuarioAutenticado } from "@/features/auth/model/auth.repository"
import { obterApiBaseUrl } from "@/shared/config/api"

export const dynamic = "force-dynamic"

async function carregarHistoricoInicial(
  usuarioId: number,
): Promise<HistoricoFuncionalAnalise | null> {
  try {
    const response = await fetch(
      `${obterApiBaseUrl()}/api/historicos-funcionais/usuario/${usuarioId}/ultimo`,
      {
        cache: "no-store",
      },
    )

    if (response.status === 404) {
      return null
    }

    const dados = (await response.json()) as HistoricoFuncionalAnalise | { detail?: string }

    if (!response.ok) {
      return null
    }

    return dados as HistoricoFuncionalAnalise
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
    return await carregarUsuarioAutenticado(token)
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
