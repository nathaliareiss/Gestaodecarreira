"use client"

import { useSearchParams } from "next/navigation"

import { AuthEntryController } from "@/features/auth/controller/auth-entry-controller"

export default function LoginPage() {
  const searchParams = useSearchParams()
  const modo = searchParams.get("modo")
  const modoLoginInicial = modo === "recuperacao" ? "recuperacao" : "login"

  return (
    <AuthEntryController
      key={modoLoginInicial}
      modoInicial="login"
      modoLoginInicial={modoLoginInicial}
    />
  )
}
