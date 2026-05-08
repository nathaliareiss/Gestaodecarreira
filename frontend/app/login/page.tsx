import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import { AUTH_USER_COOKIE_NAME, DEMO_MODE_COOKIE_NAME } from "@/shared/auth/session"
import { LoginController } from "@/features/auth/controller/login-controller"

export const dynamic = "force-dynamic"

async function usuarioJaAutenticado(): Promise<boolean> {
  const cookieStore = await cookies()
  const modoDemo = cookieStore.get(DEMO_MODE_COOKIE_NAME)?.value === "1"
  if (modoDemo) {
    return true
  }

  const usuarioId = cookieStore.get(AUTH_USER_COOKIE_NAME)?.value
  if (!usuarioId) {
    return false
  }

  return Number.isFinite(Number(usuarioId)) && Number(usuarioId) > 0
}

export default async function LoginPage() {
  if (await usuarioJaAutenticado()) {
    redirect("/usuario")
  }

  return <LoginController />
}
