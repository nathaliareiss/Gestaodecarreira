import { CarreiraFormView } from "./carreira-form-view"
import { CarreiraResultsView } from "./carreira-results-view"
import type { CadastroCarreira, ResumoCarreira } from "../../../model/carreira.model"
import type { FormEvent } from "react"

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

const blocos = [
  {
    titulo: "Backend Python",
    texto: "FastAPI recebe o JSON, usa os services existentes e devolve o resumo funcional.",
  },
  {
    titulo: "Frontend React",
    texto: "O formulario vive no cliente e faz fetch para a API com NEXT_PUBLIC_API_URL.",
  },
  {
    titulo: "Deploy separado",
    texto: "Cada pasta pode ir para um deploy diferente sem misturar runtime nem build.",
  },
]

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

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Gestao de Carreira</p>
          <h1>Visualize e teste a carreira em um front Next com backend Python.</h1>
          <p className="hero-text">
            O projeto ficou separado em duas camadas: o backend continua em Python,
            e o frontend em Next conversa com ele por HTTP para voce testar tudo de forma
            visual.
          </p>
        </div>

        <div className="hero-grid">
          {blocos.map((bloco) => (
            <article className="mini-card" key={bloco.titulo}>
              <h2>{bloco.titulo}</h2>
              <p>{bloco.texto}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="notes-grid">
        <article className="note-card">
          <p className="eyebrow">Como o front fala com o back</p>
          <h2>Fluxo de dados</h2>
          <ol>
            <li>Voce preenche o formulario no Next.</li>
            <li>O front envia um POST /api/carreira/resumo em JSON.</li>
            <li>O backend monta a Servidora e roda os calculos.</li>
            <li>A API devolve o resumo e o front organiza a resposta.</li>
          </ol>
        </article>

        <article className="note-card">
          <p className="eyebrow">Arquitetura</p>
          <h2>O que vive em cada camada</h2>
          <ul>
            <li>Model guarda os dados e o contrato.</li>
            <li>Repository faz a comunicacao HTTP.</li>
            <li>Controller coordena o estado e as acoes.</li>
            <li>View renderiza a interface sem regra de negocio.</li>
          </ul>
        </article>
      </section>

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
    </main>
  )
}

