"use client"

import { LoginView } from "../view/login-view"
import { useLoginController } from "./use-login-controller"

export function LoginController() {
  const {
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
  } = useLoginController()

  return (
    <LoginView
      dados={dados}
      recuperacao={recuperacao}
      carregando={carregando}
      recuperando={recuperando}
      erro={erro}
      erroRecuperacao={erroRecuperacao}
      mensagemRecuperacao={mensagemRecuperacao}
      onSubmit={enviarFormulario}
      onRecuperacaoSubmit={enviarRecuperacao}
      onLoginChange={(valor) => atualizarCampo("login", valor)}
      onSenhaChange={(valor) => atualizarCampo("senha", valor)}
      onRecuperacaoIdentificadorChange={(valor) =>
        atualizarCampoRecuperacao("identificador", valor)
      }
      onRecuperacaoSenhaChange={(valor) =>
        atualizarCampoRecuperacao("nova_senha", valor)
      }
    />
  )
}

