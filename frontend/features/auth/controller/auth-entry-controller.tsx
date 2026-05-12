"use client"

import { useState } from "react"

import { useLoginController } from "./use-login-controller"
import { LoginCardView } from "@/features/auth/view/login-card-view"
import { useUsuarioController } from "@/features/usuario/controller/use-usuario-controller"
import { UsuarioFormView } from "@/features/usuario/view/usuario-form-view"
import { UsuarioHeroSection } from "@/features/usuario/view/usuario-hero-section"

type ModoEntradaAuth = "login" | "cadastro"

type AuthEntryControllerProps = {
  modoInicial: ModoEntradaAuth
}

export function AuthEntryController({ modoInicial }: AuthEntryControllerProps) {
  const [modo, setModo] = useState<ModoEntradaAuth>(modoInicial)
  const login = useLoginController()
  const cadastro = useUsuarioController()

  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--register">
        <UsuarioHeroSection
          entrandoDemo={cadastro.entrandoDemo}
          onEntrarDemo={cadastro.entrarComDadosDeExemplo}
          onAbrirLogin={() => setModo("login")}
        />

        <div className="side-panel side-panel--register">
          {modo === "cadastro" ? (
            <UsuarioFormView
              cadastro={cadastro.cadastro}
              carregando={cadastro.carregando}
              erro={cadastro.erro}
              onSubmit={cadastro.enviarFormulario}
              onNomeChange={(valor) => cadastro.atualizarCampo("nome", valor)}
              onApelidoChange={(valor) => cadastro.atualizarCampo("apelido", valor)}
              onEmailChange={(valor) => cadastro.atualizarCampo("email", valor)}
              onDataExercicioChange={(valor) => cadastro.atualizarCampo("data_exercicio", valor)}
              onLoginChange={(valor) => cadastro.atualizarCampo("login", valor)}
              onSenhaChange={(valor) => cadastro.atualizarCampo("senha", valor)}
            />
          ) : (
            <LoginCardView
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
          )}
        </div>
      </section>
    </main>
  )
}
