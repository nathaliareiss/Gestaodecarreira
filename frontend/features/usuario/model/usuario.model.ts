export type UsuarioCadastro = {
  nome: string
  apelido: string
  email: string
  data_exercicio: string
  login: string
  senha: string
}

export type UsuarioConta = {
  id: number
  nome: string
  apelido: string | null
  email: string
  data_exercicio: string | null
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
  data_exercicio: "",
  login: "",
  senha: "",
}

export const USUARIO_CADASTRO_EXEMPLO: UsuarioCadastro = {
  nome: "Maria Silva",
  apelido: "Mari",
  email: "maria.silva@exemplo.com",
  data_exercicio: "2018-03-01",
  login: "maria.silva",
  senha: "senha123",
}
