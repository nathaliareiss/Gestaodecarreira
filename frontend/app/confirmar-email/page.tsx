import { ConfirmarEmailView } from "@/features/usuario/view/confirmar-email-view"

type ConfirmarEmailPageProps = {
  searchParams?: {
    token?: string | string[]
  }
}

export default function ConfirmarEmailPage({
  searchParams,
}: ConfirmarEmailPageProps) {
  const token = Array.isArray(searchParams?.token)
    ? searchParams?.token[0]
    : searchParams?.token ?? null

  return <ConfirmarEmailView token={token} />
}
