"use client"

import { useSearchParams } from "next/navigation"

import { RedefinirSenhaView } from "@/features/auth/view/redefinir-senha-view"

export default function RedefinirSenhaPage() {
  const searchParams = useSearchParams()
  const token = searchParams.get("token")

  return <RedefinirSenhaView token={token} />
}
