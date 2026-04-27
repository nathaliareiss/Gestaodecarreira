"use client"

import { useCarreiraController } from "./use-carreira-controller"
import { CarreiraPageView } from "../view/carreira-page-view"

export function CarreiraController() {
  const {
    cadastro,
    resumo,
    carregando,
    erro,
    enviarFormulario,
    usarExemplo,
    atualizarCampo,
  } = useCarreiraController()

  return (
    <CarreiraPageView
      cadastro={cadastro}
      resumo={resumo}
      carregando={carregando}
      erro={erro}
      onSubmit={enviarFormulario}
      onNomeChange={(valor) => atualizarCampo("nome", valor)}
      onDataNascimentoChange={(valor) => atualizarCampo("data_nascimento", valor)}
      onDataIngressoChange={(valor) => atualizarCampo("data_ingresso", valor)}
      onCltChange={(valor) => atualizarCampo("tem_tempo_clt_averbado", valor)}
      onUsarExemplo={usarExemplo}
    />
  )
}
