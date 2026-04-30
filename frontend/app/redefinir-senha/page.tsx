import { Suspense } from "react"

import { RedefinirSenhaPageClient } from "./redefinir-senha-page-client"

export const dynamic = "force-dynamic"

export default function RedefinirSenhaPage() {
  return (
    <Suspense fallback={<div />}>
      <RedefinirSenhaPageClient />
    </Suspense>
  )
}
