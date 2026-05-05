"use client"

import { useState, type FormEvent } from "react"
import { useRouter } from "next/navigation"

import {
  USUARIO_LOGIN_INICIAL,
  USUARIO_SOLICITACAO_RECUPERACAO_SENHA_INICIAL,
  type UsuarioLogin,
  type UsuarioSolicitacaoRecuperacaoSenha,
} from "../model/auth.model"
import {
  autenticarUsuario,
  solicitarRecuperacaoSenha,
} from "../model/auth.repository"
import {
  salvarTokenAutenticacao,
  salvarUsuarioAutenticadoCache,
} from "@/shared/auth/session"

type ModoAutenticacao = "login" | "recuperacao"

export function useLoginController() {
  const router = useRouter()
  const [modo, setModo] = useState<ModoAutenticacao>("login")
  const [dados, setDados] = useState<UsuarioLogin>(USUARIO_LOGIN_INICIAL)
  const [recuperacao, setRecuperacao] = useState<UsuarioSolicitacaoRecuperacaoSenha>(
    USUARIO_SOLICITACAO_RECUPERACAO_SENHA_INICIAL,
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

  function atualizarCampoRecuperacao<Chave extends keyof UsuarioSolicitacaoRecuperacaoSenha>(
    chave: Chave,
    valor: UsuarioSolicitacaoRecuperacaoSenha[Chave],
  ) {
    setRecuperacao((atual) => ({
      ...atual,
      [chave]: valor,
    }))
  }

  function abrirRecuperacao() {
    setModo("recuperacao")
    setErro(null)
    setErroRecuperacao(null)
    setMensagemRecuperacao(null)
  }

  function voltarParaLogin() {
    setModo("login")
    setErroRecuperacao(null)
    setMensagemRecuperacao(null)
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
      salvarUsuarioAutenticadoCache(resposta.usuario)
      router.replace("/usuario")
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao entrar.")
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
      const resposta = await solicitarRecuperacaoSenha({
        email: recuperacao.email.trim(),
      })

      setMensagemRecuperacao(resposta.message)
      setRecuperacao(USUARIO_SOLICITACAO_RECUPERACAO_SENHA_INICIAL)
    } catch (error) {
      setErroRecuperacao(
        error instanceof Error ? error.message : "Falha inesperada ao recuperar a senha.",
      )
    } finally {
      setRecuperando(false)
    }
  }

  return {
    modo,
    dados,
    recuperacao,
    carregando,
    recuperando,
    erro,
    erroRecuperacao,
    mensagemRecuperacao,
    enviarFormulario,
    enviarRecuperacao,
    abrirRecuperacao,
    voltarParaLogin,
    atualizarCampo,
    atualizarCampoRecuperacao,
  }
}
