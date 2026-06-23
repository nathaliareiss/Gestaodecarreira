"use client"

import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent, type FormEvent } from "react"

import { ApiResponseError } from "@/shared/api/client"
import type {
  HistoricoFuncionalAnalise,
  JobAgendadoResponse,
} from "../model/historico-funcional.model"
import {
  anexarAfastamentosAoHistorico,
  anexarFeriasAoHistorico,
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

function formatarErroHistorico(error: unknown, idioma: "pt-BR" | "en") {
  if (error instanceof ApiResponseError) {
    if (error.status === 401) {
      return idioma === "en"
        ? "Your session expired. Please sign in again."
        : "Sua sessão expirou. Entre novamente."
    }

    if (error.status === 404) {
      return idioma === "en"
        ? "No saved career history was found yet."
        : "Ainda não foi encontrado um histórico funcional salvo."
    }

    if (error.status === 500) {
      return idioma === "en"
        ? "The career history area is temporarily unavailable."
        : "A área de histórico funcional está temporariamente indisponível."
    }

    return error.message
  }

  if (error instanceof Error && error.message.trim().length > 0) {
    return error.message
  }

  return idioma === "en"
    ? "Unexpected failure while processing the career history."
    : "Falha inesperada ao processar o histórico funcional."
}

export function useHistoricoFuncionalController({
  usuarioId,
  historicoInicial,
}: UseHistoricoFuncionalControllerParams) {
  const [arquivo, setArquivo] = useState<File | null>(null)
  const [arquivoAfastamentos, setArquivoAfastamentos] = useState<File | null>(null)
  const [arquivoFerias, setArquivoFerias] = useState<File | null>(null)
  const [dataNascimento, setDataNascimento] = useState(historicoInicial?.data_nascimento ?? "")
  const [sexo, setSexo] = useState<"feminino" | "masculino">(
    historicoInicial?.sexo === "masculino" ? "masculino" : "feminino",
  )
  const [categoriaPrevidenciaria, setCategoriaPrevidenciaria] = useState<
    "geral" | "professor" | "seguranca" | "saude_exposicao"
  >(historicoInicial?.categoria_previdenciaria ?? "geral")
  const [anosCltAverbados, setAnosCltAverbados] = useState(
    historicoInicial?.tempo_clt_averbado_anos ?? 0,
  )
  const [historico, setHistorico] = useState<HistoricoFuncionalAnalise | null>(historicoInicial)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [mensagemProcessamento, setMensagemProcessamento] = useState<string | null>(null)
  const [modoAtualizacaoHistorico, setModoAtualizacaoHistorico] = useState(false)
  const [modoAnexoAfastamentos, setModoAnexoAfastamentos] = useState(false)
  const [modoAnexoFerias, setModoAnexoFerias] = useState(false)
  const assinaturaEnvioAutomatico = useRef<string | null>(null)
  const arquivoDownloadUrl = useMemo(() => {
    if (!arquivo) {
      return null
    }

    return URL.createObjectURL(arquivo)
  }, [arquivo])

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
        setTimeout(resolve, 1500)
      })
    }

    throw new Error("O processamento demorou mais do que o esperado.")
  }

  useEffect(() => {
    return () => {
      if (arquivoDownloadUrl) {
        URL.revokeObjectURL(arquivoDownloadUrl)
      }
    }
  }, [arquivoDownloadUrl])

  function selecionarArquivo(evento: ChangeEvent<HTMLInputElement>) {
    const selecionado = evento.target.files?.[0] ?? null
    setArquivo(selecionado)
    setModoAtualizacaoHistorico(true)
    setModoAnexoAfastamentos(false)
    setModoAnexoFerias(false)
    setErro(null)
  }

  function selecionarArquivoAfastamentos(evento: ChangeEvent<HTMLInputElement>) {
    const selecionado = evento.target.files?.[0] ?? null
    setArquivoAfastamentos(selecionado)
    setModoAnexoAfastamentos(true)
    setModoAnexoFerias(false)
    setErro(null)
  }

  function selecionarArquivoFerias(evento: ChangeEvent<HTMLInputElement>) {
    const selecionado = evento.target.files?.[0] ?? null
    setArquivoFerias(selecionado)
    setModoAnexoFerias(true)
    setModoAnexoAfastamentos(false)
    setErro(null)
  }

  function iniciarAnexoAfastamentos() {
    setModoAnexoAfastamentos(true)
    setModoAtualizacaoHistorico(false)
    setModoAnexoFerias(false)
    setErro(null)
  }

  function iniciarAnexoFerias() {
    setModoAnexoFerias(true)
    setModoAtualizacaoHistorico(false)
    setModoAnexoAfastamentos(false)
    setErro(null)
  }

  function iniciarAtualizacaoHistorico() {
    setModoAtualizacaoHistorico(true)
    setModoAnexoAfastamentos(false)
    setModoAnexoFerias(false)
    setErro(null)
  }

  function usarCltMaximo() {
    setAnosCltAverbados(10)
    setErro(null)
  }

  const criarAssinaturaHistorico = useCallback(
    () =>
      [
        arquivo?.name ?? "",
        arquivo?.size ?? 0,
        arquivo?.lastModified ?? 0,
        dataNascimento,
        sexo,
        categoriaPrevidenciaria,
        anosCltAverbados,
        usuarioId ?? "",
      ].join("|"),
    [arquivo, dataNascimento, sexo, categoriaPrevidenciaria, anosCltAverbados, usuarioId],
  )

  const criarAssinaturaAfastamentos = useCallback(
    () =>
      [
        arquivoAfastamentos?.name ?? "",
        arquivoAfastamentos?.size ?? 0,
        arquivoAfastamentos?.lastModified ?? 0,
        historico?.historico_id ?? "",
        usuarioId ?? "",
      ].join("|"),
    [arquivoAfastamentos, historico, usuarioId],
  )

  const criarAssinaturaFerias = useCallback(
    () =>
      [
        arquivoFerias?.name ?? "",
        arquivoFerias?.size ?? 0,
        arquivoFerias?.lastModified ?? 0,
        historico?.historico_id ?? "",
        usuarioId ?? "",
      ].join("|"),
    [arquivoFerias, historico, usuarioId],
  )

  const recarregarHistorico = useCallback(async () => {
    if (!usuarioId) {
      return
    }

    setCarregando(true)
    setErro(null)

    try {
      const recarregado = await buscarUltimoHistoricoFuncional(usuarioId)
      setHistorico(recarregado)
      setModoAtualizacaoHistorico(false)
      setModoAnexoAfastamentos(false)
      setModoAnexoFerias(false)
    } catch (error) {
      setErro(formatarErroHistorico(error, "pt-BR"))
    } finally {
      setCarregando(false)
    }
  }, [usuarioId])

  const submeterAnalise = useCallback(
    async (assinatura?: string) => {
      if (!usuarioId) {
        setErro("Create a user before uploading the career history.")
        return
      }

      if (!arquivo) {
        setErro("Choose a career history PDF.")
        return
      }

      if (!dataNascimento) {
        setErro("Informe a data de nascimento para calcular a aposentadoria.")
        return
      }

      setCarregando(true)
      setErro(null)
      setMensagemProcessamento("Processing the career history PDF in the background...")

      if (assinatura) {
        assinaturaEnvioAutomatico.current = assinatura
      }

      try {
        const payload = new FormData()
        payload.append("arquivo", arquivo)
        payload.append("data_nascimento", dataNascimento)
        payload.append("sexo", sexo)
        payload.append("categoria_previdenciaria", categoriaPrevidenciaria)
        payload.append("anos_clt_averbados", String(Math.min(Math.max(anosCltAverbados, 0), 10)))
        if (arquivoAfastamentos) {
          payload.append("afastamentos_arquivo", arquivoAfastamentos)
        }
        if (arquivoFerias) {
          payload.append("ferias_arquivo", arquivoFerias)
        }

        const resposta = await analisarHistoricoFuncional(payload)
        const analisado = respostaEhJob(resposta)
          ? await aguardarResultadoJob(resposta.job_id)
          : resposta

        setHistorico(analisado)
        setModoAtualizacaoHistorico(false)
        setModoAnexoAfastamentos(false)
        setModoAnexoFerias(false)
      } catch (error) {
        if (assinatura) {
          assinaturaEnvioAutomatico.current = null
        }
        setErro(formatarErroHistorico(error, "pt-BR"))
      } finally {
        setMensagemProcessamento(null)
        setCarregando(false)
      }
    },
    [arquivo, arquivoAfastamentos, arquivoFerias, anosCltAverbados, categoriaPrevidenciaria, dataNascimento, sexo, usuarioId],
  )

  const submeterAfastamentos = useCallback(
    async (assinatura?: string) => {
      if (!usuarioId) {
        setErro("Create a user before uploading leave records.")
        return
      }

      if (!historico) {
        setErro("Upload the career history first.")
        return
      }

      if (!arquivoAfastamentos) {
        setErro("Choose a leave records PDF.")
        return
      }

      setCarregando(true)
      setErro(null)
      setMensagemProcessamento("Processing the leave records PDF in the background...")

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
        setModoAnexoAfastamentos(false)
      } catch (error) {
        if (assinatura) {
          assinaturaEnvioAutomatico.current = null
        }
        setErro(formatarErroHistorico(error, "pt-BR"))
      } finally {
        setMensagemProcessamento(null)
        setCarregando(false)
      }
    },
    [arquivoAfastamentos, historico, usuarioId],
  )

  const submeterFerias = useCallback(
    async (assinatura?: string) => {
      if (!usuarioId) {
        setErro("Crie um usuario antes de enviar ferias.")
        return
      }

      if (!historico) {
        setErro("Envie o historico de carreira primeiro.")
        return
      }

      if (!arquivoFerias) {
        setErro("Escolha um PDF de ferias.")
        return
      }

      setCarregando(true)
      setErro(null)
      setMensagemProcessamento("Processando o PDF de ferias em segundo plano...")

      if (assinatura) {
        assinaturaEnvioAutomatico.current = assinatura
      }

      try {
        const payload = new FormData()
        payload.append("arquivo", arquivoFerias)
        const resposta = await anexarFeriasAoHistorico(usuarioId, payload)

        const analisado = respostaEhJob(resposta)
          ? await aguardarResultadoJob(resposta.job_id)
          : resposta

        setHistorico(analisado)
        setArquivoFerias(null)
        setModoAnexoFerias(false)
      } catch (error) {
        if (assinatura) {
          assinaturaEnvioAutomatico.current = null
        }
        setErro(formatarErroHistorico(error, "pt-BR"))
      } finally {
        setMensagemProcessamento(null)
        setCarregando(false)
      }
    },
    [arquivoFerias, historico, usuarioId],
  )

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
  }, [
    arquivo,
    dataNascimento,
    anosCltAverbados,
    sexo,
    categoriaPrevidenciaria,
    carregando,
    usuarioId,
    modoAtualizacaoHistorico,
    criarAssinaturaHistorico,
    submeterAnalise,
  ])

  useEffect(() => {
    if (historicoInicial !== null || !usuarioId) {
      return
    }

    const timer = window.setTimeout(() => {
      void recarregarHistorico()
    }, 0)

    return () => window.clearTimeout(timer)
  }, [historicoInicial, recarregarHistorico, usuarioId])

  useEffect(() => {
    if (!modoAnexoAfastamentos || !historico || !arquivoAfastamentos || carregando) {
      return
    }

    const assinatura = criarAssinaturaAfastamentos()
    if (assinaturaEnvioAutomatico.current === assinatura) {
      return
    }

    void submeterAfastamentos(assinatura)
  }, [
    arquivoAfastamentos,
    carregando,
    usuarioId,
    historico,
    modoAnexoAfastamentos,
    criarAssinaturaAfastamentos,
    submeterAfastamentos,
  ])

  useEffect(() => {
    if (!modoAnexoFerias || !historico || !arquivoFerias || carregando) {
      return
    }

    const assinatura = criarAssinaturaFerias()
    if (assinaturaEnvioAutomatico.current === assinatura) {
      return
    }

    void submeterFerias(assinatura)
  }, [
    arquivoFerias,
    carregando,
    usuarioId,
    historico,
    modoAnexoFerias,
    criarAssinaturaFerias,
    submeterFerias,
  ])

  return {
    arquivo,
    arquivoDownloadUrl,
    arquivoAfastamentos,
    arquivoFerias,
    anosCltAverbados,
    sexo,
    categoriaPrevidenciaria,
    carregando,
    dataNascimento,
    erro,
    mensagemProcessamento,
    historico,
    modoAtualizacaoHistorico,
    modoAnexoAfastamentos,
    modoAnexoFerias,
    iniciarAnexoAfastamentos,
    iniciarAnexoFerias,
    iniciarAtualizacaoHistorico,
    recarregarHistorico,
    selecionarArquivo,
    selecionarArquivoAfastamentos,
    selecionarArquivoFerias,
    setAnosCltAverbados,
    setDataNascimento,
    setSexo,
    setCategoriaPrevidenciaria,
    usarCltMaximo,
    enviarFormulario,
  }
}

