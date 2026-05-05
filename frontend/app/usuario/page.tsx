import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import { UsuarioPageController } from "@/features/usuario/controller/usuario-page-controller"
import type { UsuarioConta } from "@/features/usuario/model/usuario.model"
import { AUTH_COOKIE_NAME, AUTH_USER_COOKIE_NAME } from "@/shared/auth/session"

export const dynamic = "force-dynamic"

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

  if (!usuarioCache) {
    redirect("/login")
  }

  return <UsuarioPageController usuarioInicial={usuarioCache} historicoInicial={null} erroInicial={null} />
}
