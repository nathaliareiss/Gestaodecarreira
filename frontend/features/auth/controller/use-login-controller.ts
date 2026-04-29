"use client"

import { useState, type FormEvent } from "react"
import { useRouter } from "next/navigation"

import {
  USUARIO_LOGIN_INICIAL,
  USUARIO_RECUPERACAO_SENHA_INICIAL,
  type UsuarioLogin,
  type UsuarioRecuperacaoSenha,
} from "../model/auth.model"
import { autenticarUsuario, redefinirSenhaUsuario } from "../model/auth.repository"
import { salvarTokenAutenticacao } from "@/shared/auth/session"

export function useLoginController() {
  const router = useRouter()
  const [dados, setDados] = useState<UsuarioLogin>(USUARIO_LOGIN_INICIAL)
  const [recuperacao, setRecuperacao] = useState<UsuarioRecuperacaoSenha>(
    USUARIO_RECUPERACAO_SENHA_INICIAL,
  )
  const [carregando, setCarregando] = useState(false)
  const [recuperando, setRecuperando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [erroRecuperacao, setErroRecuperacao] = useState<string | null>(null)
  const [mensagemRecuperacao, setMensagemRecuperacao] = useState<string | null>(null)

  function atualizarCampo<Chave extends keyof UsuarioLogin>(
    chave: Chave,
    valor: UsuarioLogin[Chave],
  ) {
    setDados((atual) => ({
      ...atual,
      [chave]: valor,
    }))
  }

  function atualizarCampoRecuperacao<Chave extends keyof UsuarioRecuperacaoSenha>(
    chave: Chave,
    valor: UsuarioRecuperacaoSenha[Chave],
  ) {
    setRecuperacao((atual) => ({
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

  async function enviarRecuperacao(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setRecuperando(true)
    setErroRecuperacao(null)
    setMensagemRecuperacao(null)

    try {
      await redefinirSenhaUsuario({
        identificador: recuperacao.identificador.trim(),
        nova_senha: recuperacao.nova_senha,
      })

      setMensagemRecuperacao("Senha atualizada. Agora voce pode entrar com a nova senha.")
      setRecuperacao(USUARIO_RECUPERACAO_SENHA_INICIAL)
    } catch (error) {
      setErroRecuperacao(
        error instanceof Error ? error.message : "Falha inesperada ao recuperar a senha",
      )
    } finally {
      setRecuperando(false)
    }
  }

  return {
    dados,
    recuperacao,
    carregando,
    recuperando,
    erro,
    erroRecuperacao,
    mensagemRecuperacao,
    enviarFormulario,
    enviarRecuperacao,
    atualizarCampo,
    atualizarCampoRecuperacao,
  }
}

