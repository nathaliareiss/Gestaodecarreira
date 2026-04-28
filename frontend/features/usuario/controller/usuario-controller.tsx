"use client"

import { useUsuarioController } from "./use-usuario-controller"
import { UsuarioPageView } from "../view/usuario-page-view"

export function UsuarioController() {
  const {
    cadastro,
    carregando,
    erro,
    enviarFormulario,
    usarExemplo,
    atualizarCampo,
  } = useUsuarioController()

  return (
    <UsuarioPageView
      cadastro={cadastro}
      carregando={carregando}
      erro={erro}
      onSubmit={enviarFormulario}
      onNomeChange={(valor) => atualizarCampo("nome", valor)}
      onApelidoChange={(valor) => atualizarCampo("apelido", valor)}
      onEmailChange={(valor) => atualizarCampo("email", valor)}
      onLoginChange={(valor) => atualizarCampo("login", valor)}
      onSenhaChange={(valor) => atualizarCampo("senha", valor)}
      onUsarExemplo={usarExemplo}
    />
  )
}
