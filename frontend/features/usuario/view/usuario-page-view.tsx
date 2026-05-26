import type { FormEvent } from "react"

import type { UsuarioCadastro } from "../model/usuario.model"

import { UsuarioFormView } from "./usuario-form-view"
import { UsuarioHeroSection } from "./usuario-hero-section"

type UsuarioPageViewProps = {
  cadastro: UsuarioCadastro
  carregando: boolean
  entrandoDemo: boolean
  erro: string | null
  mensagem: string | null
  onSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onEntrarDemo: () => void
  onAbrirLogin?: () => void
  onNomeChange: (valor: string) => void
  onApelidoChange: (valor: string) => void
  onEmailChange: (valor: string) => void
  onDataExercicioChange: (valor: string) => void
  onLoginChange: (valor: string) => void
  onSenhaChange: (valor: string) => void
}

export function UsuarioPageView({
  cadastro,
  carregando,
  entrandoDemo,
  erro,
  mensagem,
  onSubmit,
  onEntrarDemo,
  onAbrirLogin,
  onNomeChange,
  onApelidoChange,
  onEmailChange,
  onDataExercicioChange,
  onLoginChange,
  onSenhaChange,
}: UsuarioPageViewProps) {
  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--register">
        <UsuarioHeroSection
          entrandoDemo={entrandoDemo}
          onEntrarDemo={onEntrarDemo}
          onAbrirLogin={onAbrirLogin}
        />

        <div className="side-panel side-panel--register">
          <UsuarioFormView
            cadastro={cadastro}
            carregando={carregando}
            erro={erro}
            mensagem={mensagem}
            onSubmit={onSubmit}
            onNomeChange={onNomeChange}
            onApelidoChange={onApelidoChange}
            onEmailChange={onEmailChange}
            onDataExercicioChange={onDataExercicioChange}
            onLoginChange={onLoginChange}
            onSenhaChange={onSenhaChange}
          />
        </div>
      </section>
    </main>
  )
}
