"use client"

import { useRouter } from "next/navigation"
import { useState, type FormEvent } from "react"

import {
  USUARIO_CADASTRO_INICIAL,
  type UsuarioCadastro,
} from "../model/usuario.model"
import { criarUsuario } from "../model/usuario.repository"
import { salvarSessaoDemo } from "@/shared/auth/session"
import { ApiResponseError } from "@/shared/api/client"
import { useLanguage } from "@/shared/i18n/language-provider"

type CadastroErroAcao = {
  label: string
  href: string
}

export type CadastroErroMensagem = {
  message: string
  action?: CadastroErroAcao
}

export function useUsuarioController() {
  const router = useRouter()
  const { texts } = useLanguage()
  const registerTexts = texts.registerForm
  const [cadastro, setCadastro] = useState<UsuarioCadastro>(USUARIO_CADASTRO_INICIAL)
  const [carregando, setCarregando] = useState(false)
  const [entrandoDemo, setEntrandoDemo] = useState(false)
  const [erro, setErro] = useState<CadastroErroMensagem | null>(null)
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
      return registerTexts.requiredFields
    }

    if (senha.length < 6) {
      return registerTexts.passwordMinLength
    }

    if (!cadastro.aceite_politica_privacidade) {
      return registerTexts.privacyConsentRequired
    }

    return null
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    const erroValidacao = validarCadastro()
    if (erroValidacao) {
      setErro({ message: erroValidacao })
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
        aceite_politica_privacidade: cadastro.aceite_politica_privacidade,
      })
      router.replace("/login")
    } catch (error) {
      if (error instanceof ApiResponseError && error.status === 409) {
        const mensagemErro = error.message.toLowerCase()
        if (mensagemErro.includes("login")) {
          setErro({ message: registerTexts.loginAlreadyRegistered })
        } else if (mensagemErro.includes("email")) {
          setErro({
            message: registerTexts.emailAlreadyRegisteredPrefix,
            action: {
              label: registerTexts.emailAlreadyRegisteredLink,
              href: "/login?modo=recuperacao",
            },
          })
        } else {
          setErro({ message: registerTexts.unexpectedSave })
        }
      } else {
        setErro({ message: registerTexts.unexpectedSave })
      }
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

