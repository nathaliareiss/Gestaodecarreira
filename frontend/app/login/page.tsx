import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import { AUTH_COOKIE_NAME } from "@/shared/auth/session"
import { carregarUsuarioAutenticado } from "@/features/auth/model/auth.repository"
import { LoginController } from "@/features/auth/controller/login-controller"

export const dynamic = "force-dynamic"

async function usuarioJaAutenticado(): Promise<boolean> {
  const cookieStore = await cookies()
  const token = cookieStore.get(AUTH_COOKIE_NAME)?.value
  if (!token) {
    return false
  }

  try {
    await carregarUsuarioAutenticado(token)
    return true
  } catch {
    return false
  }
}

export default async function LoginPage() {
  if (await usuarioJaAutenticado()) {
    redirect("/usuario")
  }

  return <LoginController />
}
