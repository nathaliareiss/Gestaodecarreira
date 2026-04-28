"use client"

import { useState, type FormEvent } from "react"
import { useRouter } from "next/navigation"

import {
  USUARIO_CADASTRO_EXEMPLO,
  USUARIO_CADASTRO_INICIAL,
  type UsuarioCadastro,
} from "../model/usuario.model"
import { criarUsuario } from "../model/usuario.repository"

export function useUsuarioController() {
  const router = useRouter()
  const [cadastro, setCadastro] = useState<UsuarioCadastro>(USUARIO_CADASTRO_INICIAL)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  function atualizarCampo<Chave extends keyof UsuarioCadastro>(
    chave: Chave,
    valor: UsuarioCadastro[Chave],
  ) {
    setCadastro((atual) => ({
      ...atual,
      [chave]: valor,
    }))
  }

  function usarExemplo() {
    setCadastro(USUARIO_CADASTRO_EXEMPLO)
    setErro(null)
  }

  function validarCadastro() {
    const nome = cadastro.nome.trim()
    const email = cadastro.email.trim()
    const login = cadastro.login.trim()
    const senha = cadastro.senha

    if (!nome || !email || !login || !senha) {
      return "Preencha nome, email, login e senha."
    }

    if (!email.includes("@")) {
      return "Informe um email valido."
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

    try {
      await criarUsuario({
        nome: cadastro.nome.trim(),
        apelido: cadastro.apelido.trim(),
        email: cadastro.email.trim(),
        login: cadastro.login.trim(),
        senha: cadastro.senha,
      })
      router.push("/usuario")
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao salvar")
    } finally {
      setCarregando(false)
    }
  }

  return {
    cadastro,
    carregando,
    erro,
    enviarFormulario,
    usarExemplo,
    atualizarCampo,
  }
}
