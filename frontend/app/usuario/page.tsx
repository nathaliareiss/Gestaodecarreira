import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import type { UsuarioConta } from "@/features/usuario/model/usuario.model"
import { UsuarioPageController } from "@/features/usuario/controller/usuario-page-controller"
import type { HistoricoFuncionalAnalise } from "@/features/historico-funcional/model/historico-funcional.model"
import { AUTH_COOKIE_NAME } from "@/shared/auth/session"
import { apiFetch } from "@/shared/api/client"
import { carregarUsuarioAutenticado } from "@/features/auth/model/auth.repository"

export const dynamic = "force-dynamic"

async function carregarHistoricoInicial(
  usuarioId: number,
): Promise<HistoricoFuncionalAnalise | null> {
  try {
    const response = await apiFetch(
      `/api/historicos-funcionais/usuario/${usuarioId}/ultimo`,
      {
        cache: "no-store",
      },
    )

    if (!response.ok) {
      return null
    }

    return (await response.json()) as HistoricoFuncionalAnalise
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

