"use client"

import { useState, type FormEvent } from "react"

import { buscarResumoCarreira } from "../model/carreira.repository"
import {
  CADASTRO_CARREIRA_INICIAL,
  type CadastroCarreira,
  type ResumoCarreira,
} from "../model/carreira.model"

export function useCarreiraController() {
  const [cadastro, setCadastro] = useState<CadastroCarreira>(CADASTRO_CARREIRA_INICIAL)
  const [resumo, setResumo] = useState<ResumoCarreira | null>(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setCarregando(true)
    setErro(null)

    try {
      const dados = await buscarResumoCarreira(cadastro)
      setResumo(dados)
    } catch (error) {
      setResumo(null)
      setErro(error instanceof Error ? error.message : "Falha inesperada")
    } finally {
      setCarregando(false)
    }
  }

  function usarExemplo() {
    setCadastro(CADASTRO_CARREIRA_INICIAL)
    setErro(null)
    setResumo(null)
  }

  function atualizarCampo<Chave extends keyof CadastroCarreira>(
    chave: Chave,
    valor: CadastroCarreira[Chave],
  ) {
    setCadastro((atual) => ({
      ...atual,
      [chave]: valor,
    }))
  }

  return {
    cadastro,
    resumo,
    carregando,
    erro,
    enviarFormulario,
    usarExemplo,
    atualizarCampo,
  }
}
