import { ConfirmarEmailView } from "@/features/usuario/view/confirmar-email-view"

export const dynamic = "force-dynamic"

type ConfirmarEmailPageProps = {
  searchParams?: Promise<{
    token?: string | string[]
  }>
}

export default async function ConfirmarEmailPage({ searchParams }: ConfirmarEmailPageProps) {
  const parametros = (await searchParams) ?? {}
  const token = Array.isArray(parametros.token) ? parametros.token[0] : parametros.token ?? null

  return <ConfirmarEmailView token={token} />
}
