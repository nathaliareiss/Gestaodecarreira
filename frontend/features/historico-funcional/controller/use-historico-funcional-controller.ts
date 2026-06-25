"use client"

import { useCallback, useEffect, useRef, useState, type ChangeEvent, type FormEvent, type RefObject } from "react"

import { ApiResponseError } from "@/shared/api/client"
import type { SiteLanguage } from "@/shared/i18n/messages"
import type {
  HistoricoFuncionalAnalise,
  JobAgendadoResponse,
} from "../model/historico-funcional.model"
import {
  analisarHistoricoFuncional,
  consultarStatusJobHistorico,
  buscarUltimoHistoricoFuncional,
  limparHistoricoFuncional,
} from "../model/historico-funcional.repository"

type UseHistoricoFuncionalControllerParams = {
  usuarioId: number | null
  historicoInicial: HistoricoFuncionalAnalise | null
  idioma: SiteLanguage
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
  idioma,
}: UseHistoricoFuncionalControllerParams) {
  const [arquivo, setArquivo] = useState<File | null>(null)
  const [arquivoAfastamentos, setArquivoAfastamentos] = useState<File | null>(null)
  const [arquivosFerias, setArquivosFerias] = useState<File[]>([])
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
  const [mensagemSucesso, setMensagemSucesso] = useState<string | null>(null)
  const arquivoInputRef = useRef<HTMLInputElement | null>(null)
  const afastamentosInputRef = useRef<HTMLInputElement | null>(null)
  const feriasInputRef = useRef<HTMLInputElement | null>(null)

  function limparInput(ref: RefObject<HTMLInputElement | null>) {
    if (ref.current) {
      ref.current.value = ""
    }
  }

  const limparEntradaArquivos = useCallback(() => {
    limparInput(arquivoInputRef)
    limparInput(afastamentosInputRef)
    limparInput(feriasInputRef)
  }, [])

  const resetarFormularioDeEnvio = useCallback(() => {
    setArquivo(null)
    setArquivoAfastamentos(null)
    setArquivosFerias([])
    setDataNascimento(historicoInicial?.data_nascimento ?? "")
    setSexo(historicoInicial?.sexo === "masculino" ? "masculino" : "feminino")
    setCategoriaPrevidenciaria(historicoInicial?.categoria_previdenciaria ?? "geral")
    setAnosCltAverbados(historicoInicial?.tempo_clt_averbado_anos ?? 0)
    setErro(null)
    setMensagemProcessamento(null)
    setMensagemSucesso(null)
    limparEntradaArquivos()
  }, [historicoInicial, limparEntradaArquivos])

  const limparArquivosSelecionados = useCallback(() => {
    setArquivo(null)
    setArquivoAfastamentos(null)
    setArquivosFerias([])
    setErro(null)
    setMensagemProcessamento(null)
    setMensagemSucesso(null)
    limparEntradaArquivos()
  }, [limparEntradaArquivos])

  function arquivoEhPdf(arquivoSelecionado: File) {
    return arquivoSelecionado.type === "application/pdf" || arquivoSelecionado.name.toLowerCase().endsWith(".pdf")
  }

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

  function selecionarArquivo(evento: ChangeEvent<HTMLInputElement>) {
    const selecionado = evento.target.files?.[0] ?? null
    if (selecionado && !arquivoEhPdf(selecionado)) {
      setArquivo(null)
      limparInput(arquivoInputRef)
      setErro(idioma === "en" ? "Select valid PDF files only." : "Selecione apenas arquivos PDF válidos.")
      return
    }

    setArquivo(selecionado)
    setErro(null)
    setMensagemSucesso(null)
  }

  function selecionarArquivoAfastamentos(evento: ChangeEvent<HTMLInputElement>) {
    const selecionado = evento.target.files?.[0] ?? null
    if (selecionado && !arquivoEhPdf(selecionado)) {
      setArquivoAfastamentos(null)
      limparInput(afastamentosInputRef)
      setErro(idioma === "en" ? "Select valid PDF files only." : "Selecione apenas arquivos PDF válidos.")
      return
    }

    setArquivoAfastamentos(selecionado)
    setErro(null)
    setMensagemSucesso(null)
  }

  function selecionarArquivoFerias(evento: ChangeEvent<HTMLInputElement>) {
    const selecionados = Array.from(evento.target.files ?? [])

    if (selecionados.some((arquivoSelecionado) => !arquivoEhPdf(arquivoSelecionado))) {
      setArquivosFerias([])
      limparInput(feriasInputRef)
      setErro(idioma === "en" ? "Select valid PDF files only." : "Selecione apenas arquivos PDF válidos.")
      return
    }

    if (selecionados.length > 3) {
      setArquivosFerias(selecionados.slice(0, 3))
      setErro(
        idioma === "en"
          ? "Select at most 3 vacation PDFs at a time."
          : "Selecione no máximo 3 PDFs de férias por vez.",
      )
      setMensagemSucesso(null)
      return
    }

    setArquivosFerias(selecionados)
    setErro(null)
    setMensagemSucesso(null)
  }

  function removerArquivoPrincipal() {
    setArquivo(null)
    limparInput(arquivoInputRef)
    setErro(null)
    setMensagemSucesso(null)
  }

  function removerArquivoAfastamentos() {
    setArquivoAfastamentos(null)
    limparInput(afastamentosInputRef)
    setErro(null)
    setMensagemSucesso(null)
  }

  function removerArquivoFerias(indice: number) {
    setArquivosFerias((atual) => atual.filter((_, indiceAtual) => indiceAtual !== indice))
    limparInput(feriasInputRef)
    setErro(null)
    setMensagemSucesso(null)
  }

  const limparHistorico = useCallback(async () => {
    if (!usuarioId) {
      setErro(idioma === "en" ? "Create a user before clearing the history." : "Crie um usuário antes de limpar o histórico.")
      return
    }

    const confirmado = window.confirm(
      idioma === "en"
        ? "Delete the uploaded career history? This action removes the saved analysis and linked PDFs."
        : "Apagar o histórico de carreira enviado? Esta ação remove a análise salva e os PDFs vinculados.",
    )
    if (!confirmado) {
      return
    }

    setCarregando(true)
    setErro(null)
    setMensagemProcessamento(
      idioma === "en" ? "Clearing the career history..." : "Limpando histórico de carreira...",
    )
    setMensagemSucesso(null)

    try {
      await limparHistoricoFuncional(usuarioId)
      setHistorico(null)
      limparArquivosSelecionados()
    } catch (error) {
      setErro(formatarErroHistorico(error, idioma))
    } finally {
      setMensagemProcessamento(null)
      setCarregando(false)
    }
  }, [idioma, limparArquivosSelecionados, usuarioId])

  function usarCltMaximo() {
    setAnosCltAverbados(10)
    setErro(null)
  }

  const recarregarHistorico = useCallback(async () => {
    if (!usuarioId) {
      return
    }

    setCarregando(true)
    setErro(null)

    try {
      const recarregado = await buscarUltimoHistoricoFuncional(usuarioId)
      setHistorico(recarregado)
    } catch (error) {
      setErro(formatarErroHistorico(error, idioma))
    } finally {
      setCarregando(false)
    }
  }, [idioma, usuarioId])

  const submeterAnalise = useCallback(async () => {
    if (!usuarioId) {
      setErro(idioma === "en" ? "Create a user before uploading the career history." : "Crie um usuário antes de enviar o histórico funcional.")
      return
    }

    if (!arquivo) {
      setErro(idioma === "en" ? "Select the career history PDF to continue." : "Selecione o PDF do histórico funcional para continuar.")
      return
    }

    if (!dataNascimento) {
      setErro(
        idioma === "en"
          ? "Fill in the date of birth before sending the documents."
          : "Preencha a data de nascimento antes de enviar os documentos.",
      )
      return
    }

    if (arquivosFerias.length > 3) {
      setErro(idioma === "en" ? "Select at most 3 vacation PDFs at a time." : "Selecione no máximo 3 PDFs de férias por vez.")
      return
    }

    setCarregando(true)
    setErro(null)
    setMensagemSucesso(null)
    setMensagemProcessamento(idioma === "en" ? "Sending documents..." : "Enviando documentos...")

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

      for (const arquivoFerias of arquivosFerias) {
        payload.append("ferias_arquivos", arquivoFerias)
      }

      const resposta = await analisarHistoricoFuncional(payload)
      const analisado = respostaEhJob(resposta)
        ? await aguardarResultadoJob(resposta.job_id)
        : resposta

      setHistorico(analisado)
      limparArquivosSelecionados()
      setMensagemSucesso(
        idioma === "en" ? "Documents sent successfully." : "Documentos enviados com sucesso.",
      )
    } catch (error) {
      setErro(formatarErroHistorico(error, idioma))
    } finally {
      setMensagemProcessamento(null)
      setCarregando(false)
    }
  }, [
    arquivo,
    arquivoAfastamentos,
    arquivosFerias,
    anosCltAverbados,
    categoriaPrevidenciaria,
    dataNascimento,
    idioma,
    limparArquivosSelecionados,
    sexo,
    usuarioId,
  ])

  async function enviarFormulario(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    if (!evento.currentTarget.checkValidity()) {
      evento.currentTarget.reportValidity()
      return
    }
    await submeterAnalise()
  }

  useEffect(() => {
    if (historicoInicial !== null || !usuarioId) {
      return
    }

    const timer = window.setTimeout(() => {
      void recarregarHistorico()
    }, 0)

    return () => window.clearTimeout(timer)
  }, [historicoInicial, recarregarHistorico, usuarioId])

  return {
    arquivo,
    arquivoAfastamentos,
    arquivosFerias,
    anosCltAverbados,
    sexo,
    categoriaPrevidenciaria,
    carregando,
    dataNascimento,
    erro,
    mensagemProcessamento,
    mensagemSucesso,
    historico,
    limparHistorico,
    arquivoInputRef,
    afastamentosInputRef,
    feriasInputRef,
    selecionarArquivo,
    selecionarArquivoAfastamentos,
    selecionarArquivoFerias,
    removerArquivoPrincipal,
    removerArquivoAfastamentos,
    removerArquivoFerias,
    limparFormulario: resetarFormularioDeEnvio,
    setAnosCltAverbados,
    setDataNascimento,
    setSexo,
    setCategoriaPrevidenciaria,
    usarCltMaximo,
    enviarFormulario,
  }
}

