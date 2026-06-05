import { RedefinirSenhaView } from "@/features/auth/view/redefinir-senha-view"

export const dynamic = "force-dynamic"

type DefinirSenhaPageProps = {
  searchParams?: {
    token?: string | string[]
  }
}

export default function DefinirSenhaPage({ searchParams }: DefinirSenhaPageProps) {
  const token = Array.isArray(searchParams?.token) ? searchParams?.token[0] : searchParams?.token ?? null

  return <RedefinirSenhaView token={token} />
}
