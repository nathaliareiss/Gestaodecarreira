import { cookies } from "next/headers"
import { redirect } from "next/navigation"

import { AuthEntryController } from "@/features/auth/controller/auth-entry-controller"
import { DEMO_MODE_COOKIE_NAME } from "@/shared/auth/session"

export const dynamic = "force-dynamic"

export default async function HomePage() {
  const cookieStore = await cookies()
  const modoDemo = cookieStore.get(DEMO_MODE_COOKIE_NAME)?.value === "1"
  if (modoDemo) {
    redirect("/usuario")
  }

  return <AuthEntryController modoInicial="login" />
}
