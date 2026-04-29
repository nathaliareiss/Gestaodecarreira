import { Suspense } from "react"

import { RedefinirSenhaPageClient } from "./redefinir-senha-page-client"

export default function RedefinirSenhaPage() {
  return (
    <Suspense fallback={<div />}>
      <RedefinirSenhaPageClient />
    </Suspense>
  )
}
