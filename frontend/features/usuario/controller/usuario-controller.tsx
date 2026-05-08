"use client"

import { useUsuarioController } from "./use-usuario-controller"
import { UsuarioPageView } from "../view/usuario-page-view"

export function UsuarioController() {
  const {
    cadastro,
    carregando,
    entrandoDemo,
    erro,
    enviarFormulario,
    entrarComDadosDeExemplo,
    atualizarCampo,
  } = useUsuarioController()

  return (
    <UsuarioPageView
      cadastro={cadastro}
      carregando={carregando}
      entrandoDemo={entrandoDemo}
      erro={erro}
      onSubmit={enviarFormulario}
      onEntrarDemo={entrarComDadosDeExemplo}
      onNomeChange={(valor) => atualizarCampo("nome", valor)}
      onApelidoChange={(valor) => atualizarCampo("apelido", valor)}
      onEmailChange={(valor) => atualizarCampo("email", valor)}
      onDataExercicioChange={(valor) => atualizarCampo("data_exercicio", valor)}
      onLoginChange={(valor) => atualizarCampo("login", valor)}
      onSenhaChange={(valor) => atualizarCampo("senha", valor)}
    />
  )
}
