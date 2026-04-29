import type { CadastroCarreira, ResumoCarreira } from "../model/carreira.model"
import type { FormEvent } from "react"

import { CarreiraHeroSection } from "./sections/carreira-hero-section"
import { CarreiraWorkbenchView } from "./carreira-workbench-view"

type CarreiraPageViewProps = {
  cadastro: CadastroCarreira
  resumo: ResumoCarreira | null
  carregando: boolean
  erro: string | null
  onSubmit: (evento: FormEvent<HTMLFormElement>) => void
  onNomeChange: (valor: string) => void
  onDataNascimentoChange: (valor: string) => void
  onDataIngressoChange: (valor: string) => void
  onCltChange: (valor: boolean) => void
  onUsarExemplo: () => void
}

export function CarreiraPageView({
  cadastro,
  resumo,
  carregando,
  erro,
  onSubmit,
  onNomeChange,
  onDataNascimentoChange,
  onDataIngressoChange,
  onCltChange,
  onUsarExemplo,
}: CarreiraPageViewProps) {
  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />
      <CarreiraHeroSection />
      <CarreiraWorkbenchView
        cadastro={cadastro}
        resumo={resumo}
        carregando={carregando}
        erro={erro}
        onSubmit={onSubmit}
        onNomeChange={onNomeChange}
        onDataNascimentoChange={onDataNascimentoChange}
        onDataIngressoChange={onDataIngressoChange}
        onCltChange={onCltChange}
        onUsarExemplo={onUsarExemplo}
      />
    </main>
  )
}
