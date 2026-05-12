import { encerrarSessao } from "./auth.repository"
import { removerSessaoDemo, removerUsuarioAutenticadoId } from "@/shared/auth/session"

export async function limparSessaoAutenticada() {
  try {
    await encerrarSessao()
  } catch {
    // Se o backend já tiver invalidado a sessão, seguimos limpando o estado local.
  } finally {
    removerSessaoDemo()
    removerUsuarioAutenticadoId()
  }
}
