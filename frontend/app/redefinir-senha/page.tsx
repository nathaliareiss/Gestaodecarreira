import { RedefinirSenhaView } from "@/features/auth/view/redefinir-senha-view"

export const dynamic = "force-dynamic"

type RedefinirSenhaPageProps = {
  searchParams?: {
    token?: string | string[]
  }
}

export default function RedefinirSenhaPage({ searchParams }: RedefinirSenhaPageProps) {
  const token = Array.isArray(searchParams?.token) ? searchParams?.token[0] : searchParams?.token ?? null

  return <RedefinirSenhaView token={token} />
}
