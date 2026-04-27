import type { FormEvent } from "react"

import type { CadastroCarreira, ResumoCarreira } from "../model/carreira.model"

import { CarreiraFormView } from "./carreira-form-view"
import { CarreiraResultsView } from "./carreira-results-view"

type CarreiraWorkbenchViewProps = {
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

export function CarreiraWorkbenchView({
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
}: CarreiraWorkbenchViewProps) {
  return (
    <div className="workbench">
      <CarreiraFormView
        cadastro={cadastro}
        carregando={carregando}
        erro={erro}
        onSubmit={onSubmit}
        onNomeChange={onNomeChange}
        onDataNascimentoChange={onDataNascimentoChange}
        onDataIngressoChange={onDataIngressoChange}
        onCltChange={onCltChange}
        onUsarExemplo={onUsarExemplo}
      />
      <CarreiraResultsView resumo={resumo} />
    </div>
  )
}
