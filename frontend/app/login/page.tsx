import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import { AUTH_COOKIE_NAME, DEMO_MODE_COOKIE_NAME } from "@/shared/auth/session"
import { obterApiBaseUrl } from "@/shared/config/api"
import { LoginController } from "@/features/auth/controller/login-controller"

export const dynamic = "force-dynamic"

async function usuarioJaAutenticado(): Promise<boolean> {
  const cookieStore = await cookies()
  const modoDemo = cookieStore.get(DEMO_MODE_COOKIE_NAME)?.value === "1"
  if (modoDemo) {
    return true
  }

  const token = cookieStore.get(AUTH_COOKIE_NAME)?.value
  if (!token) {
    return false
  }

  try {
    const response = await fetch(`${obterApiBaseUrl()}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    })

    return response.ok
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
