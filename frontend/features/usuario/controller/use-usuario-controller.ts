"use client"

import { useRouter } from "next/navigation"
import { useState, type FormEvent } from "react"

import {
  USUARIO_CADASTRO_INICIAL,
  type UsuarioCadastro,
} from "../model/usuario.model"
import { criarUsuario } from "../model/usuario.repository"
import { salvarSessaoDemo } from "@/shared/auth/session"

export function useUsuarioController() {
  const router = useRouter()
  const [cadastro, setCadastro] = useState<UsuarioCadastro>(USUARIO_CADASTRO_INICIAL)
  const [carregando, setCarregando] = useState(false)
  const [entrandoDemo, setEntrandoDemo] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [mensagem, setMensagem] = useState<string | null>(null)

  function atualizarCampo<Chave extends keyof UsuarioCadastro>(
    chave: Chave,
    valor: UsuarioCadastro[Chave],
  ) {
    setCadastro((atual) => ({
      ...atual,
      [chave]: valor,
    }))
  }

  function entrarComDadosDeExemplo() {
    setErro(null)
    setMensagem(null)
    setEntrandoDemo(true)
    try {
      salvarSessaoDemo()
      router.replace("/usuario")
    } finally {
      setEntrandoDemo(false)
    }
  }

  function validarCadastro() {
    const nome = cadastro.nome.trim()
    const email = cadastro.email.trim()
    const dataExercicio = cadastro.data_exercicio
    const login = cadastro.login.trim()
    const senha = cadastro.senha

    if (!nome || !email || !dataExercicio || !login || !senha) {
      return "Preencha nome, e-mail, data de exercício, login e senha."
    }

    if (senha.length < 6) {
      return "A senha precisa ter pelo menos 6 caracteres."
    }

    return null
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    const erroValidacao = validarCadastro()
    if (erroValidacao) {
      setErro(erroValidacao)
      return
    }

    setCarregando(true)
    setErro(null)
    setMensagem(null)

    try {
      await criarUsuario({
        nome: cadastro.nome.trim(),
        apelido: cadastro.apelido.trim(),
        email: cadastro.email.trim(),
        data_exercicio: cadastro.data_exercicio,
        login: cadastro.login.trim(),
        senha: cadastro.senha,
      })
      setMensagem("Cadastro concluído com sucesso. Agora você pode entrar com seu login.")
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao salvar.")
    } finally {
      setCarregando(false)
    }
  }

  return {
    cadastro,
    carregando,
    entrandoDemo,
    erro,
    mensagem,
    enviarFormulario,
    entrarComDadosDeExemplo,
    atualizarCampo,
  }
}

