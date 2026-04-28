export type UsuarioCadastro = {
  nome: string
  apelido: string
  email: string
  login: string
  senha: string
}

export type UsuarioConta = {
  id: number
  nome: string
  apelido: string | null
  email: string
  login: string
  senha_cadastrada: boolean
  email_confirmado: boolean
  criado_em: string
  confirmado_em: string | null
}

export const USUARIO_CADASTRO_INICIAL: UsuarioCadastro = {
  nome: "",
  apelido: "",
  email: "",
  login: "",
  senha: "",
}

export const USUARIO_CADASTRO_EXEMPLO: UsuarioCadastro = {
  nome: "Maria Silva",
  apelido: "Mari",
  email: "maria.silva@exemplo.com",
  login: "maria.silva",
  senha: "senha123",
}
