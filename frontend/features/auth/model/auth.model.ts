import type { UsuarioConta } from "@/features/usuario/model/usuario.model"

export type UsuarioLogin = {
  login: string
  senha: string
}

export type UsuarioAuthResponse = {
  access_token: string
  token_type: string
  usuario: UsuarioConta
}

export const USUARIO_LOGIN_INICIAL: UsuarioLogin = {
  login: "",
  senha: "",
}

