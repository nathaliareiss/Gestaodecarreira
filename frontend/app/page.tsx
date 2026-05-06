import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import { UsuarioController } from "@/features/usuario/controller/usuario-controller"
import { DEMO_MODE_COOKIE_NAME } from "@/shared/auth/session"

export const dynamic = "force-dynamic"

export default async function HomePage() {
  const cookieStore = await cookies()
  const modoDemo = cookieStore.get(DEMO_MODE_COOKIE_NAME)?.value === "1"
  if (modoDemo) {
    redirect("/usuario")
  }

  return <UsuarioController />
}
