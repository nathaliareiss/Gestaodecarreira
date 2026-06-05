import { AuthEntryController } from "@/features/auth/controller/auth-entry-controller"

type LoginPageProps = {
  searchParams?: {
    modo?: string | string[]
  }
}

export default function LoginPage({ searchParams }: LoginPageProps) {
  const modo = Array.isArray(searchParams?.modo) ? searchParams.modo[0] : searchParams?.modo
  const modoLoginInicial = modo === "recuperacao" ? "recuperacao" : "login"

  return <AuthEntryController modoInicial="login" modoLoginInicial={modoLoginInicial} />
}
