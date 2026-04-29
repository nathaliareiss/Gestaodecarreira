"use client"

import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from "react"

import type {
  HistoricoFuncionalAnalise,
  HistoricoFuncionalUpload,
} from "../model/historico-funcional.model"
import {
  anexarAfastamentosAoHistorico,
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
  const [arquivoAfastamentos, setArquivoAfastamentos] = useState<File | null>(null)
  const [arquivoAfastamentosDownloadUrl, setArquivoAfastamentosDownloadUrl] = useState<string | null>(
    null,
  )
  const [dataNascimento, setDataNascimento] = useState(historicoInicial?.data_nascimento ?? "")
  const [anosCltAverbados, setAnosCltAverbados] = useState(
    historicoInicial?.tempo_clt_averbado_anos ?? 0,
  )
  const [historico, setHistorico] = useState<HistoricoFuncionalAnalise | null>(historicoInicial)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [mostrarUpload, setMostrarUpload] = useState(historicoInicial === null)
  const [modoAtualizacaoHistorico, setModoAtualizacaoHistorico] = useState(historicoInicial === null)
  const [modoAnexoAfastamentos, setModoAnexoAfastamentos] = useState(historicoInicial !== null)
  const assinaturaEnvioAutomatico = useRef<string | null>(null)

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

  useEffect(() => {
    if (!arquivoAfastamentos) {
      setArquivoAfastamentosDownloadUrl(null)
      return
    }

    const url = URL.createObjectURL(arquivoAfastamentos)
    setArquivoAfastamentosDownloadUrl(url)

    return () => {
      URL.revokeObjectURL(url)
    }
  }, [arquivoAfastamentos])

  function selecionarArquivo(evento: ChangeEvent<HTMLInputElement>) {
    const selecionado = evento.target.files?.[0] ?? null
    setArquivo(selecionado)
    setModoAtualizacaoHistorico(true)
    setModoAnexoAfastamentos(false)
    setMostrarUpload(true)
    setErro(null)
  }

  function selecionarArquivoAfastamentos(evento: ChangeEvent<HTMLInputElement>) {
    const selecionado = evento.target.files?.[0] ?? null
    setArquivoAfastamentos(selecionado)
    setModoAnexoAfastamentos(true)
    setMostrarUpload(true)
    setErro(null)
  }

  function iniciarAnexoAfastamentos() {
    setModoAnexoAfastamentos(true)
    setModoAtualizacaoHistorico(false)
    setMostrarUpload(true)
    setErro(null)
  }

  function iniciarAtualizacaoHistorico() {
    setModoAtualizacaoHistorico(true)
    setModoAnexoAfastamentos(false)
    setMostrarUpload(true)
    setErro(null)
  }

  function usarCltMaximo() {
    setAnosCltAverbados(10)
    setErro(null)
  }

  function criarAssinaturaHistorico() {
    return [
      arquivo?.name ?? "",
      arquivo?.size ?? 0,
      arquivo?.lastModified ?? 0,
      dataNascimento,
      anosCltAverbados,
      usuarioId ?? "",
    ].join("|")
  }

  function criarAssinaturaAfastamentos() {
    return [
      arquivoAfastamentos?.name ?? "",
      arquivoAfastamentos?.size ?? 0,
      arquivoAfastamentos?.lastModified ?? 0,
      historico?.historico_id ?? "",
      usuarioId ?? "",
    ].join("|")
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
        setModoAtualizacaoHistorico(false)
        setModoAnexoAfastamentos(true)
      }
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao recarregar.")
    } finally {
      setCarregando(false)
    }
  }

  async function submeterAnalise(assinatura?: string) {
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

    if (assinatura) {
      assinaturaEnvioAutomatico.current = assinatura
    }

    try {
      const arquivoBase64 = await lerArquivoComoBase64(arquivo)
      const afastamentosArquivoBase64 = arquivoAfastamentos
        ? await lerArquivoComoBase64(arquivoAfastamentos)
        : null
      const payload: HistoricoFuncionalUpload = {
        usuario_id: usuarioId,
        arquivo_nome: arquivo.name,
        arquivo_base64: arquivoBase64,
        data_nascimento: dataNascimento,
        anos_clt_averbados: Math.min(Math.max(anosCltAverbados, 0), 10),
        afastamentos_arquivo_nome: arquivoAfastamentos?.name ?? null,
        afastamentos_arquivo_base64: afastamentosArquivoBase64,
      }

      const analisado = await analisarHistoricoFuncional(payload)
      setHistorico(analisado)
      setModoAtualizacaoHistorico(false)
      setModoAnexoAfastamentos(true)
      setMostrarUpload(false)
    } catch (error) {
      if (assinatura) {
        assinaturaEnvioAutomatico.current = null
      }
      setErro(error instanceof Error ? error.message : "Falha inesperada ao analisar.")
    } finally {
      setCarregando(false)
    }
  }

  async function submeterAfastamentos(assinatura?: string) {
    if (!usuarioId) {
      setErro("Cadastre um usuário antes de enviar os afastamentos.")
      return
    }

    if (!historico) {
      setErro("Envie primeiro o histórico funcional.")
      return
    }

    if (!arquivoAfastamentos) {
      setErro("Escolha um PDF de afastamentos.")
      return
    }

    setCarregando(true)
    setErro(null)

    if (assinatura) {
      assinaturaEnvioAutomatico.current = assinatura
    }

    try {
      const arquivoBase64 = await lerArquivoComoBase64(arquivoAfastamentos)
      const analisado = await anexarAfastamentosAoHistorico(usuarioId, {
        arquivo_nome: arquivoAfastamentos.name,
        arquivo_base64: arquivoBase64,
      })

      setHistorico(analisado)
      setArquivoAfastamentos(null)
      setModoAnexoAfastamentos(true)
      setMostrarUpload(false)
    } catch (error) {
      if (assinatura) {
        assinaturaEnvioAutomatico.current = null
      }
      setErro(error instanceof Error ? error.message : "Falha inesperada ao analisar os afastamentos.")
    } finally {
      setCarregando(false)
    }
  }

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    await submeterAnalise()
  }

  useEffect(() => {
    if (!modoAtualizacaoHistorico || !arquivo || !dataNascimento || carregando) {
      return
    }

    const assinatura = criarAssinaturaHistorico()
    if (assinaturaEnvioAutomatico.current === assinatura) {
      return
    }

    void submeterAnalise(assinatura)
  }, [arquivo, dataNascimento, anosCltAverbados, carregando, usuarioId, modoAtualizacaoHistorico])

  useEffect(() => {
    if (!modoAnexoAfastamentos || !historico || !arquivoAfastamentos || carregando) {
      return
    }

    const assinatura = criarAssinaturaAfastamentos()
    if (assinaturaEnvioAutomatico.current === assinatura) {
      return
    }

    void submeterAfastamentos(assinatura)
  }, [arquivoAfastamentos, carregando, usuarioId, historico, modoAnexoAfastamentos])

  return {
    arquivo,
    arquivoDownloadUrl,
    arquivoAfastamentos,
    arquivoAfastamentosDownloadUrl,
    anosCltAverbados,
    carregando,
    dataNascimento,
    erro,
    historico,
    mostrarUpload,
    modoAtualizacaoHistorico,
    modoAnexoAfastamentos,
    iniciarAnexoAfastamentos,
    iniciarAtualizacaoHistorico,
    recarregarHistorico,
    selecionarArquivo,
    selecionarArquivoAfastamentos,
    setAnosCltAverbados,
    setDataNascimento,
    setMostrarUpload,
    usarCltMaximo,
    enviarFormulario,
  }
}
