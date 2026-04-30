"use client"

import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from "react"

import type {
  HistoricoFuncionalAnalise,
  JobAgendadoResponse,
} from "../model/historico-funcional.model"
import {
  anexarAfastamentosAoHistorico,
  analisarHistoricoFuncional,
  consultarStatusJobHistorico,
  buscarUltimoHistoricoFuncional,
} from "../model/historico-funcional.repository"

type UseHistoricoFuncionalControllerParams = {
  usuarioId: number | null
  historicoInicial: HistoricoFuncionalAnalise | null
}

function respostaEhJob(
  resposta: HistoricoFuncionalAnalise | JobAgendadoResponse,
): resposta is JobAgendadoResponse {
  return "job_id" in resposta
}

export function useHistoricoFuncionalController({
  usuarioId,
  historicoInicial,
}: UseHistoricoFuncionalControllerParams) {
  const [arquivo, setArquivo] = useState<File | null>(null)
  const [arquivoDownloadUrl, setArquivoDownloadUrl] = useState<string | null>(null)
  const [arquivoAfastamentos, setArquivoAfastamentos] = useState<File | null>(null)
  const [dataNascimento, setDataNascimento] = useState(historicoInicial?.data_nascimento ?? "")
  const [anosCltAverbados, setAnosCltAverbados] = useState(
    historicoInicial?.tempo_clt_averbado_anos ?? 0,
  )
  const [historico, setHistorico] = useState<HistoricoFuncionalAnalise | null>(historicoInicial)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [mensagemProcessamento, setMensagemProcessamento] = useState<string | null>(null)
  const [modoAtualizacaoHistorico, setModoAtualizacaoHistorico] = useState(historicoInicial === null)
  const [modoAnexoAfastamentos, setModoAnexoAfastamentos] = useState(historicoInicial !== null)
  const assinaturaEnvioAutomatico = useRef<string | null>(null)

  async function aguardarResultadoJob(jobId: string) {
    for (let tentativas = 0; tentativas < 60; tentativas += 1) {
      const status = await consultarStatusJobHistorico(jobId)

      if (status.status === "finished") {
        if (!status.result) {
          throw new Error("O processamento terminou sem retornar resultado.")
        }

        return status.result
      }

      if (status.status === "failed") {
        throw new Error(status.detail ?? "O processamento em segundo plano falhou.")
      }

      await new Promise((resolve) => {
        window.setTimeout(resolve, 1500)
      })
    }

    throw new Error("O processamento demorou mais do que o esperado.")
  }

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
    setModoAtualizacaoHistorico(true)
    setModoAnexoAfastamentos(false)
    setErro(null)
  }

  function selecionarArquivoAfastamentos(evento: ChangeEvent<HTMLInputElement>) {
    const selecionado = evento.target.files?.[0] ?? null
    setArquivoAfastamentos(selecionado)
    setModoAnexoAfastamentos(true)
    setErro(null)
  }

  function iniciarAnexoAfastamentos() {
    setModoAnexoAfastamentos(true)
    setModoAtualizacaoHistorico(false)
    setErro(null)
  }

  function iniciarAtualizacaoHistorico() {
    setModoAtualizacaoHistorico(true)
    setModoAnexoAfastamentos(false)
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
    setMensagemProcessamento("Processando o PDF do histórico funcional em segundo plano...")

    if (assinatura) {
      assinaturaEnvioAutomatico.current = assinatura
    }

    try {
      const payload = new FormData()
      payload.append("usuario_id", String(usuarioId))
      payload.append("arquivo", arquivo)
      payload.append("data_nascimento", dataNascimento)
      payload.append("anos_clt_averbados", String(Math.min(Math.max(anosCltAverbados, 0), 10)))
      if (arquivoAfastamentos) {
        payload.append("afastamentos_arquivo", arquivoAfastamentos)
      }

      const resposta = await analisarHistoricoFuncional(payload)
      const analisado = respostaEhJob(resposta)
        ? await aguardarResultadoJob(resposta.job_id)
        : resposta

      setHistorico(analisado)
      setModoAtualizacaoHistorico(false)
      setModoAnexoAfastamentos(true)
    } catch (error) {
      if (assinatura) {
        assinaturaEnvioAutomatico.current = null
      }
      setErro(error instanceof Error ? error.message : "Falha inesperada ao analisar.")
    } finally {
      setMensagemProcessamento(null)
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
    setMensagemProcessamento("Processando o PDF dos afastamentos em segundo plano...")

    if (assinatura) {
      assinaturaEnvioAutomatico.current = assinatura
    }

    try {
      const payload = new FormData()
      payload.append("arquivo", arquivoAfastamentos)
      const resposta = await anexarAfastamentosAoHistorico(usuarioId, payload)

      const analisado = respostaEhJob(resposta)
        ? await aguardarResultadoJob(resposta.job_id)
        : resposta

      setHistorico(analisado)
      setArquivoAfastamentos(null)
      setModoAnexoAfastamentos(true)
    } catch (error) {
      if (assinatura) {
        assinaturaEnvioAutomatico.current = null
      }
      setErro(error instanceof Error ? error.message : "Falha inesperada ao analisar os afastamentos.")
    } finally {
      setMensagemProcessamento(null)
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
    anosCltAverbados,
    carregando,
    dataNascimento,
    erro,
    mensagemProcessamento,
    historico,
    modoAtualizacaoHistorico,
    modoAnexoAfastamentos,
    iniciarAnexoAfastamentos,
    iniciarAtualizacaoHistorico,
    recarregarHistorico,
    selecionarArquivo,
    selecionarArquivoAfastamentos,
    setAnosCltAverbados,
    setDataNascimento,
    usarCltMaximo,
    enviarFormulario,
  }
}

