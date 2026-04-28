import type { FormEvent } from "react"

import type { UsuarioCadastro } from "../model/usuario.model"

import { UsuarioFormView } from "./usuario-form-view"
import { UsuarioHeroSection } from "./usuario-hero-section"

type UsuarioPageViewProps = {
  cadastro: UsuarioCadastro
  carregando: boolean
  erro: string | null
  onSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onNomeChange: (valor: string) => void
  onApelidoChange: (valor: string) => void
  onEmailChange: (valor: string) => void
  onLoginChange: (valor: string) => void
  onSenhaChange: (valor: string) => void
  onUsarExemplo: () => void
}

export function UsuarioPageView({
  cadastro,
  carregando,
  erro,
  onSubmit,
  onNomeChange,
  onApelidoChange,
  onEmailChange,
  onLoginChange,
  onSenhaChange,
  onUsarExemplo,
}: UsuarioPageViewProps) {
  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />
      <UsuarioHeroSection />
      <section className="workbench workbench--single">
        <UsuarioFormView
          cadastro={cadastro}
          carregando={carregando}
          erro={erro}
          onSubmit={onSubmit}
          onNomeChange={onNomeChange}
          onApelidoChange={onApelidoChange}
          onEmailChange={onEmailChange}
          onLoginChange={onLoginChange}
          onSenhaChange={onSenhaChange}
          onUsarExemplo={onUsarExemplo}
        />
      </section>
    </main>
  )
}
