"use client"

import { useEffect, useState, type ChangeEvent, type FormEvent } from "react"

import type {
  HistoricoFuncionalAnalise,
  HistoricoFuncionalUpload,
} from "../model/historico-funcional.model"
import {
  analisarHistoricoFuncional,
  buscarUltimoHistoricoFuncional,
} from "../model/historico-funcional.repository"

type UseHistoricoFuncionalControllerParams = {
  usuarioId: number | null
  historicoInicial: HistoricoFuncionalAnalise | null
}

function lerArquivoComoBase64(arquivo: File) {
  return new Promise<string>((resolve, reject) => {
    const leitor = new FileReader()

    leitor.onerror = () => {
      reject(new Error("Não foi possível ler o PDF selecionado."))
    }

    leitor.onload = () => {
      const resultado = leitor.result
      if (typeof resultado !== "string") {
        reject(new Error("Não foi possível converter o PDF para base64."))
        return
      }

      resolve(resultado.split(",")[1] ?? resultado)
    }

    leitor.readAsDataURL(arquivo)
  })
}

export function useHistoricoFuncionalController({
  usuarioId,
  historicoInicial,
}: UseHistoricoFuncionalControllerParams) {
  const [arquivo, setArquivo] = useState<File | null>(null)
  const [arquivoDownloadUrl, setArquivoDownloadUrl] = useState<string | null>(null)
  const [dataNascimento, setDataNascimento] = useState(historicoInicial?.data_nascimento ?? "")
  const [anosCltAverbados, setAnosCltAverbados] = useState(
    historicoInicial?.tempo_clt_averbado_anos ?? 0,
  )
  const [historico, setHistorico] = useState<HistoricoFuncionalAnalise | null>(historicoInicial)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [mostrarUpload, setMostrarUpload] = useState(historicoInicial === null)

  useEffect(() => {
    if (!arquivo) {
      setArquivoDownloadUrl(null)
      return
    }

    const url = URL.createObjectURL(arquivo)
    setArquivoDownloadUrl(url)

    return () => {
      URL.revokeObjectURL(url)
    }
  }, [arquivo])

  function selecionarArquivo(evento: ChangeEvent<HTMLInputElement>) {
    const selecionado = evento.target.files?.[0] ?? null
    setArquivo(selecionado)
    setMostrarUpload(true)
    setErro(null)
  }

  function usarCltMaximo() {
    setAnosCltAverbados(10)
    setErro(null)
  }

  async function recarregarHistorico() {
    if (!usuarioId) {
      return
    }

    setCarregando(true)
    setErro(null)

    try {
      const recarregado = await buscarUltimoHistoricoFuncional(usuarioId)
      setHistorico(recarregado)
      if (recarregado) {
        setMostrarUpload(false)
      }
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao recarregar")
    } finally {
      setCarregando(false)
    }
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()

    if (!usuarioId) {
      setErro("Cadastre um usuário antes de enviar o histórico funcional.")
      return
    }

    if (!arquivo) {
      setErro("Escolha um PDF do histórico funcional.")
      return
    }

    if (!dataNascimento) {
      setErro("Informe a data de nascimento para calcular a aposentadoria.")
      return
    }

    setCarregando(true)
    setErro(null)

    try {
      const arquivoBase64 = await lerArquivoComoBase64(arquivo)
      const payload: HistoricoFuncionalUpload = {
        usuario_id: usuarioId,
        arquivo_nome: arquivo.name,
        arquivo_base64: arquivoBase64,
        data_nascimento: dataNascimento,
        anos_clt_averbados: Math.min(Math.max(anosCltAverbados, 0), 10),
      }

      const analisado = await analisarHistoricoFuncional(payload)
      setHistorico(analisado)
      setMostrarUpload(false)
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao analisar.")
    } finally {
      setCarregando(false)
    }
  }

  return {
    arquivo,
    arquivoDownloadUrl,
    anosCltAverbados,
    carregando,
    dataNascimento,
    erro,
    historico,
    mostrarUpload,
    recarregarHistorico,
    selecionarArquivo,
    setAnosCltAverbados,
    setDataNascimento,
    setMostrarUpload,
    usarCltMaximo,
    enviarFormulario,
  }
}
