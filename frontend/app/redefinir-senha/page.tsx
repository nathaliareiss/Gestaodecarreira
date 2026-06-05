import { RedefinirSenhaView } from "@/features/auth/view/redefinir-senha-view"

export const dynamic = "force-dynamic"

type RedefinirSenhaPageProps = {
  searchParams?: Promise<{
    token?: string | string[]
  }>
}

export default async function RedefinirSenhaPage({ searchParams }: RedefinirSenhaPageProps) {
  const parametros = (await searchParams) ?? {}
  const token = Array.isArray(parametros.token) ? parametros.token[0] : parametros.token ?? null

  return <RedefinirSenhaView token={token} />
}
