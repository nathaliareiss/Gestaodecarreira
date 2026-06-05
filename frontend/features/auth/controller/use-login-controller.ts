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
  reenviarConfirmacaoEmail,
  solicitarRecuperacaoSenha,
} from "../model/auth.repository"
import {
  removerSessaoDemo,
  salvarSessaoDemo,
} from "@/shared/auth/session"
import { useLanguage } from "@/shared/i18n/language-provider"

type ModoAutenticacao = "login" | "recuperacao"

type UseLoginControllerOptions = {
  modoInicial?: ModoAutenticacao
}

export function useLoginController({ modoInicial = "login" }: UseLoginControllerOptions = {}) {
  const router = useRouter()
  const { texts } = useLanguage()
  const authTexts = texts.authCard
  const [modo, setModo] = useState<ModoAutenticacao>(modoInicial)
  const [dados, setDados] = useState<UsuarioLogin>(USUARIO_LOGIN_INICIAL)
  const [recuperacao, setRecuperacao] = useState<UsuarioSolicitacaoRecuperacaoSenha>(
    USUARIO_SOLICITACAO_RECUPERACAO_SENHA_INICIAL,
  )
  const [carregando, setCarregando] = useState(false)
  const [entrandoDemo, setEntrandoDemo] = useState(false)
  const [recuperando, setRecuperando] = useState(false)
  const [reenviandoConfirmacao, setReenviandoConfirmacao] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [mensagemConfirmacao, setMensagemConfirmacao] = useState<string | null>(null)
  const [erroConfirmacao, setErroConfirmacao] = useState<string | null>(null)
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
    if (chave === "login") {
      setErroConfirmacao(null)
      setMensagemConfirmacao(null)
    }
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
    setErroConfirmacao(null)
    setMensagemConfirmacao(null)
    setErroRecuperacao(null)
    setMensagemRecuperacao(null)
  }

  function voltarParaLogin() {
    setModo("login")
    setErroConfirmacao(null)
    setMensagemConfirmacao(null)
    setErroRecuperacao(null)
    setMensagemRecuperacao(null)
  }

  async function reenviarConfirmacao() {
    const identificador = dados.login.trim()
    if (!identificador) {
      setErroConfirmacao(authTexts.enterLoginOrEmailToResend)
      setMensagemConfirmacao(null)
      return
    }

    setReenviandoConfirmacao(true)
    setErroConfirmacao(null)
    setMensagemConfirmacao(null)

    try {
      const resposta = await reenviarConfirmacaoEmail({ identificador })
      setMensagemConfirmacao(resposta.message)
    } catch (error) {
      setErroConfirmacao(error instanceof Error ? error.message : authTexts.unexpectedResendConfirmation)
    } finally {
      setReenviandoConfirmacao(false)
    }
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setCarregando(true)
    setErro(null)

    try {
      await autenticarUsuario({
        login: dados.login.trim(),
        senha: dados.senha,
      })

      removerSessaoDemo()
      router.replace("/usuario")
    } catch (error) {
      setErro(error instanceof Error ? error.message : authTexts.unexpectedSignin)
    } finally {
      setCarregando(false)
    }
  }

  function entrarComDadosDeExemplo() {
    setErro(null)
    setErroConfirmacao(null)
    setMensagemConfirmacao(null)
    setErroRecuperacao(null)
    setMensagemRecuperacao(null)
    setEntrandoDemo(true)

    try {
      removerSessaoDemo()
      salvarSessaoDemo()
      router.replace("/usuario")
    } finally {
      setEntrandoDemo(false)
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
      setErroRecuperacao(error instanceof Error ? error.message : authTexts.unexpectedRecovery)
    } finally {
      setRecuperando(false)
    }
  }

  return {
    modo,
    dados,
    recuperacao,
    carregando,
    entrandoDemo,
    reenviandoConfirmacao,
    recuperando,
    erro,
    mensagemConfirmacao,
    erroConfirmacao,
    erroRecuperacao,
    mensagemRecuperacao,
    enviarFormulario,
    entrarComDadosDeExemplo,
    enviarRecuperacao,
    reenviarConfirmacao,
    abrirRecuperacao,
    voltarParaLogin,
    atualizarCampo,
    atualizarCampoRecuperacao,
  }
}
