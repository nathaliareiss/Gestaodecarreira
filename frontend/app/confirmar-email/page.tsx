import { Suspense } from "react"

import { ConfirmarEmailPageClient } from "./confirmar-email-page-client"

export const dynamic = "force-dynamic"

export default function ConfirmarEmailPage() {
  return (
    <Suspense fallback={<div />}>
      <ConfirmarEmailPageClient />
    </Suspense>
  )
}
