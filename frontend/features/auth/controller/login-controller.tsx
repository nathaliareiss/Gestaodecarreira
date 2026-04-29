"use client"

import { LoginView } from "../view/login-view"
import { useLoginController } from "./use-login-controller"

export function LoginController() {
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
