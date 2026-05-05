"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

import { LoginView } from "../view/login-view"
import { useLoginController } from "./use-login-controller"

export function LoginController() {
  const router = useRouter()
  const {
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
  } = useLoginController()

  useEffect(() => {
    router.prefetch("/usuario")
  }, [router])

  return (
    <LoginView
      modo={modo}
      dados={dados}
      recuperacao={recuperacao}
      carregando={carregando}
      recuperando={recuperando}
      erro={erro}
      erroRecuperacao={erroRecuperacao}
      mensagemRecuperacao={mensagemRecuperacao}
      onSubmit={enviarFormulario}
      onRecuperacaoSubmit={enviarRecuperacao}
      onAbrirRecuperacao={abrirRecuperacao}
      onVoltarLogin={voltarParaLogin}
      onLoginChange={(valor) => atualizarCampo("login", valor)}
      onSenhaChange={(valor) => atualizarCampo("senha", valor)}
      onRecuperacaoEmailChange={(valor) => atualizarCampoRecuperacao("email", valor)}
    />
  )
}
