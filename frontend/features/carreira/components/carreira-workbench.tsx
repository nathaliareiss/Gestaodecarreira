"use client"

import { useState, type FormEvent } from "react"

import { buscarResumoCarreira } from "../carreira.api"
import { CADASTRO_INICIAL, type CadastroCarreiraRequest } from "../carreira.types"
import type { ResumoCarreiraResponse } from "../carreira.types"
import { CarreiraForm } from "./carreira-form"
import { CarreiraResults } from "./carreira-results"

export function CarreiraWorkbench() {
  const [form, setForm] = useState<CadastroCarreiraRequest>(CADASTRO_INICIAL)
  const [resumo, setResumo] = useState<ResumoCarreiraResponse | null>(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setCarregando(true)
    setErro(null)

    try {
      const dados = await buscarResumoCarreira(form)
      setResumo(dados)
    } catch (error) {
      setResumo(null)
      setErro(error instanceof Error ? error.message : "Falha inesperada")
    } finally {
      setCarregando(false)
    }
  }

  function carregarExemplo() {
    setForm(CADASTRO_INICIAL)
    setErro(null)
    setResumo(null)
  }

  return (
    <div className="workbench">
      <CarreiraForm
        form={form}
        carregando={carregando}
        erro={erro}
        onSubmit={enviarFormulario}
        onNomeChange={(valor) => setForm((atual) => ({ ...atual, nome: valor }))}
        onDataNascimentoChange={(valor) =>
          setForm((atual) => ({ ...atual, data_nascimento: valor }))
        }
        onDataIngressoChange={(valor) =>
          setForm((atual) => ({ ...atual, data_ingresso: valor }))
        }
        onCltChange={(valor) =>
          setForm((atual) => ({ ...atual, tem_tempo_clt_averbado: valor }))
        }
        onUsarExemplo={carregarExemplo}
      />

      <CarreiraResults resumo={resumo} />
    </div>
  )
}
