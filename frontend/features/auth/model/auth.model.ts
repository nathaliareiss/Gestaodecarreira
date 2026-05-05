import type { UsuarioConta } from "@/features/usuario/model/usuario.model"

export type UsuarioLogin = {
  login: string
  senha: string
}

export type UsuarioSolicitacaoRecuperacaoSenha = {
  email: string
}

export type UsuarioReenviarConfirmacaoEmail = {
  identificador: string
}

export type UsuarioRedefinicaoSenha = {
  token: string
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

export const USUARIO_SOLICITACAO_RECUPERACAO_SENHA_INICIAL: UsuarioSolicitacaoRecuperacaoSenha =
  {
    email: "",
  }

export const USUARIO_REDEFINICAO_SENHA_INICIAL: UsuarioRedefinicaoSenha = {
  token: "",
  nova_senha: "",
}

