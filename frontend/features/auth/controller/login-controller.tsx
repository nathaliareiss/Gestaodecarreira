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
    reenviandoConfirmacao,
    recuperando,
    erro,
    mensagemConfirmacao,
    erroConfirmacao,
    erroRecuperacao,
    mensagemRecuperacao,
    enviarFormulario,
    enviarRecuperacao,
    reenviarConfirmacao,
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
      reenviandoConfirmacao={reenviandoConfirmacao}
      recuperando={recuperando}
      erro={erro}
      mensagemConfirmacao={mensagemConfirmacao}
      erroConfirmacao={erroConfirmacao}
      erroRecuperacao={erroRecuperacao}
      mensagemRecuperacao={mensagemRecuperacao}
      onSubmit={enviarFormulario}
      onRecuperacaoSubmit={enviarRecuperacao}
      onReenviarConfirmacao={reenviarConfirmacao}
      onAbrirRecuperacao={abrirRecuperacao}
      onVoltarLogin={voltarParaLogin}
      onLoginChange={(valor) => atualizarCampo("login", valor)}
      onSenhaChange={(valor) => atualizarCampo("senha", valor)}
      onRecuperacaoEmailChange={(valor) => atualizarCampoRecuperacao("email", valor)}
    />
  )
}
