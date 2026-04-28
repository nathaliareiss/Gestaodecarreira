"use client"

import { useState, type FormEvent } from "react"
import { useRouter } from "next/navigation"

import {
  USUARIO_LOGIN_INICIAL,
  type UsuarioLogin,
} from "../model/auth.model"
import { autenticarUsuario } from "../model/auth.repository"
import { salvarTokenAutenticacao } from "@/shared/auth/session"

export function useLoginController() {
  const router = useRouter()
  const [dados, setDados] = useState<UsuarioLogin>(USUARIO_LOGIN_INICIAL)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  function atualizarCampo<Chave extends keyof UsuarioLogin>(
    chave: Chave,
    valor: UsuarioLogin[Chave],
  ) {
    setDados((atual) => ({
      ...atual,
      [chave]: valor,
    }))
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setCarregando(true)
    setErro(null)

    try {
      const resposta = await autenticarUsuario({
        login: dados.login.trim(),
        senha: dados.senha,
      })

      salvarTokenAutenticacao(resposta.access_token)
      router.push("/usuario")
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao entrar")
    } finally {
      setCarregando(false)
    }
  }

  return {
    dados,
    carregando,
    erro,
    enviarFormulario,
    atualizarCampo,
  }
}

