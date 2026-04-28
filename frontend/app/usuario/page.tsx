import { obterApiBaseUrl } from "@/shared/config/api"

import type { UsuarioConta } from "@/features/usuario/model/usuario.model"
import { UsuarioPageController } from "@/features/usuario/controller/usuario-page-controller"

export const dynamic = "force-dynamic"

async function carregarUsuarioInicial(): Promise<{
  usuario: UsuarioConta | null
  erro: string | null
}> {
  try {
    const response = await fetch(`${obterApiBaseUrl()}/api/usuarios/ultimo`, {
      cache: "no-store",
    })

    if (response.status === 404) {
      return { usuario: null, erro: null }
    }

    const dados = (await response.json()) as UsuarioConta | { detail?: string }

    if (!response.ok) {
      return {
        usuario: null,
        erro:
          dados && "detail" in dados ? dados.detail ?? "Falha ao carregar usuario" : "Falha ao carregar usuario",
      }
    }

    return { usuario: dados as UsuarioConta, erro: null }
  } catch (error) {
    return {
      usuario: null,
      erro: error instanceof Error ? error.message : "Falha inesperada ao carregar usuario",
    }
  }
}

export default async function UsuarioPage() {
  const { usuario, erro } = await carregarUsuarioInicial()

  return <UsuarioPageController usuarioInicial={usuario} erroInicial={erro} />
}
