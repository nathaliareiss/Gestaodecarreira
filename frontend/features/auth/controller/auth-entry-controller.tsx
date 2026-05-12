"use client"

import { useState } from "react"

import { LoginView } from "../view/login-view"
import { useLoginController } from "./use-login-controller"
import { UsuarioPageView } from "@/features/usuario/view/usuario-page-view"
import { useUsuarioController } from "@/features/usuario/controller/use-usuario-controller"

type ModoEntradaAuth = "login" | "cadastro"

type AuthEntryControllerProps = {
  modoInicial: ModoEntradaAuth
}

export function AuthEntryController({ modoInicial }: AuthEntryControllerProps) {
  const [modo, setModo] = useState<ModoEntradaAuth>(modoInicial)
  const login = useLoginController()
  const cadastro = useUsuarioController()

  if (modo === "login") {
    return (
      <LoginView
        modo={login.modo}
        dados={login.dados}
        recuperacao={login.recuperacao}
        carregando={login.carregando}
        entrandoDemo={login.entrandoDemo}
        reenviandoConfirmacao={login.reenviandoConfirmacao}
        recuperando={login.recuperando}
        erro={login.erro}
        mensagemConfirmacao={login.mensagemConfirmacao}
        erroConfirmacao={login.erroConfirmacao}
        erroRecuperacao={login.erroRecuperacao}
        mensagemRecuperacao={login.mensagemRecuperacao}
        onSubmit={login.enviarFormulario}
        onEntrarDemo={login.entrarComDadosDeExemplo}
        onRecuperacaoSubmit={login.enviarRecuperacao}
        onReenviarConfirmacao={login.reenviarConfirmacao}
        onAbrirRecuperacao={login.abrirRecuperacao}
        onAbrirCadastro={() => setModo("cadastro")}
        onVoltarLogin={login.voltarParaLogin}
        onLoginChange={(valor) => login.atualizarCampo("login", valor)}
        onSenhaChange={(valor) => login.atualizarCampo("senha", valor)}
        onRecuperacaoEmailChange={(valor) => login.atualizarCampoRecuperacao("email", valor)}
      />
    )
  }

  return (
    <UsuarioPageView
      cadastro={cadastro.cadastro}
      carregando={cadastro.carregando}
      entrandoDemo={cadastro.entrandoDemo}
      erro={cadastro.erro}
      onSubmit={cadastro.enviarFormulario}
      onEntrarDemo={cadastro.entrarComDadosDeExemplo}
      onAbrirLogin={() => setModo("login")}
      onNomeChange={(valor) => cadastro.atualizarCampo("nome", valor)}
      onApelidoChange={(valor) => cadastro.atualizarCampo("apelido", valor)}
      onEmailChange={(valor) => cadastro.atualizarCampo("email", valor)}
      onDataExercicioChange={(valor) => cadastro.atualizarCampo("data_exercicio", valor)}
      onLoginChange={(valor) => cadastro.atualizarCampo("login", valor)}
      onSenhaChange={(valor) => cadastro.atualizarCampo("senha", valor)}
    />
  )
}
