import type { UsuarioConta } from "@/features/usuario/model/usuario.model"

export type UsuarioLogin = {
  login: string
  senha: string
}

export type UsuarioRecuperacaoSenha = {
  identificador: string
  nova_senha: string
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

export const USUARIO_RECUPERACAO_SENHA_INICIAL: UsuarioRecuperacaoSenha = {
  identificador: "",
  nova_senha: "",
}

