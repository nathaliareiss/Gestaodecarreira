"use client"

import { useSearchParams } from "next/navigation"

import { ConfirmarEmailView } from "@/features/usuario/view/confirmar-email-view"

export default function ConfirmarEmailPage() {
  const searchParams = useSearchParams()
  const token = searchParams.get("token")

  return <ConfirmarEmailView token={token} />
}
