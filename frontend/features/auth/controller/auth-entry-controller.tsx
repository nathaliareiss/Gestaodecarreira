"use client"

import { useEffect, useState } from "react"

import { useLoginController } from "./use-login-controller"
import { AuthHeroSection } from "@/features/auth/view/auth-hero-section"
import { LoginCardView } from "@/features/auth/view/login-card-view"
import { useUsuarioController } from "@/features/usuario/controller/use-usuario-controller"
import { UsuarioFormView } from "@/features/usuario/view/usuario-form-view"
import { UsuarioHeroSection } from "@/features/usuario/view/usuario-hero-section"
import { removerUsuarioAutenticadoId } from "@/shared/auth/session"

type ModoEntradaAuth = "login" | "cadastro"

type AuthEntryControllerProps = {
  modoInicial: ModoEntradaAuth
  modoLoginInicial?: "login" | "recuperacao"
}

export function AuthEntryController({ modoInicial, modoLoginInicial = "login" }: AuthEntryControllerProps) {
  const [modo, setModo] = useState<ModoEntradaAuth>(modoInicial)
  const login = useLoginController({ modoInicial: modoLoginInicial })
  const cadastro = useUsuarioController()

  useEffect(() => {
    removerUsuarioAutenticadoId()
  }, [])

  return (
    <main className="page-shell page-shell--auth">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--auth">
        {modo === "cadastro" ? (
          <UsuarioHeroSection
            entrandoDemo={cadastro.entrandoDemo}
            onEntrarDemo={cadastro.entrarComDadosDeExemplo}
            onAbrirLogin={() => setModo("login")}
          />
        ) : (
          <AuthHeroSection
            entrandoDemo={login.entrandoDemo}
            onEntrarDemo={login.entrarComDadosDeExemplo}
            onAbrirCadastro={() => setModo("cadastro")}
          />
        )}

        <div className={`auth-panel ${modo === "cadastro" ? "auth-panel--register" : "auth-panel--login"}`}>
          {modo === "cadastro" ? (
            <UsuarioFormView
              cadastro={cadastro.cadastro}
              carregando={cadastro.carregando}
              erro={cadastro.erro}
              mensagem={cadastro.mensagem}
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
              reenviandoConfirmacao={login.reenviandoConfirmacao}
              recuperando={login.recuperando}
              erro={login.erro}
              mensagemConfirmacao={login.mensagemConfirmacao}
              erroConfirmacao={login.erroConfirmacao}
              erroRecuperacao={login.erroRecuperacao}
              mensagemRecuperacao={login.mensagemRecuperacao}
              onSubmit={login.enviarFormulario}
              onRecuperacaoSubmit={login.enviarRecuperacao}
              onReenviarConfirmacao={login.reenviarConfirmacao}
              onAbrirRecuperacao={login.abrirRecuperacao}
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
