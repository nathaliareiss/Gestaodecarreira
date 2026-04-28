"use client"

import { LoginView } from "../view/login-view"
import { useLoginController } from "./use-login-controller"

export function LoginController() {
  const { dados, carregando, erro, enviarFormulario, atualizarCampo } =
    useLoginController()

  return (
    <LoginView
      dados={dados}
      carregando={carregando}
      erro={erro}
      onSubmit={enviarFormulario}
      onLoginChange={(valor) => atualizarCampo("login", valor)}
      onSenhaChange={(valor) => atualizarCampo("senha", valor)}
    />
  )
}

