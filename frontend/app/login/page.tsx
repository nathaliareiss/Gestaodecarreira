import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import { AUTH_TOKEN_COOKIE_NAME, DEMO_MODE_COOKIE_NAME } from "@/shared/auth/session"
import { LoginController } from "@/features/auth/controller/login-controller"

export const dynamic = "force-dynamic"

async function usuarioJaAutenticado(): Promise<boolean> {
  const cookieStore = await cookies()
  const modoDemo = cookieStore.get(DEMO_MODE_COOKIE_NAME)?.value === "1"
  if (modoDemo) {
    return true
  }

  return Boolean(cookieStore.get(AUTH_TOKEN_COOKIE_NAME)?.value)
}

export default async function LoginPage() {
  if (await usuarioJaAutenticado()) {
    redirect("/usuario")
  }

  return <LoginController />
}
