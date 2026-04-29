"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState } from "react"

import type { HistoricoFuncionalAnalise } from "@/features/historico-funcional/model/historico-funcional.model"
import { HistoricoFuncionalView } from "@/features/historico-funcional/view/historico-funcional-view"
import {
  carregarUsuarioAutenticado,
  encerrarSessao,
} from "@/features/auth/model/auth.repository"
import { type UsuarioConta } from "@/features/usuario/model/usuario.model"
import { removerUsuarioMaisRecente } from "@/features/usuario/model/usuario.repository"
import {
  obterTokenAutenticacao,
  removerTokenAutenticacao,
} from "@/shared/auth/session"

function formatarData(valor: string | null) {
  if (!valor) {
    return "-"
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(valor))
}

function formatarDataCurta(valor: string | null) {
  if (!valor) {
    return "-"
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "medium",
    timeZone: "UTC",
  }).format(new Date(valor))
}

type UsuarioPageControllerProps = {
  usuarioInicial: UsuarioConta | null
  historicoInicial: HistoricoFuncionalAnalise | null
  erroInicial: string | null
}

export function UsuarioPageController({
  usuarioInicial,
  historicoInicial,
  erroInicial,
}: UsuarioPageControllerProps) {
  const router = useRouter()
  const [usuario, setUsuario] = useState<UsuarioConta | null>(usuarioInicial)
  const [abaAtiva, setAbaAtiva] = useState<"perfil" | "historico">("perfil")
  const [erro, setErro] = useState<string | null>(erroInicial)
  const [carregando, setCarregando] = useState(false)
  const [removendo, setRemovendo] = useState(false)
  const [saindo, setSaindo] = useState(false)

  async function recarregarUsuario() {
    const token = obterTokenAutenticacao()
    if (!token) {
      router.push("/login")
      return
    }

    setCarregando(true)
    setErro(null)

    try {
      const dados = await carregarUsuarioAutenticado(token)
      setUsuario(dados)
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao carregar.")
    } finally {
      setCarregando(false)
    }
  }

  async function excluirCadastro() {
    setRemovendo(true)
    setErro(null)

    try {
      await removerUsuarioMaisRecente()
      setUsuario(null)
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao remover.")
    } finally {
      setRemovendo(false)
    }
  }

  async function sair() {
    const token = obterTokenAutenticacao()

    setSaindo(true)
    setErro(null)

    try {
      if (token) {
        await encerrarSessao(token)
      }
    } catch {
      // Se a chamada remota falhar, a sessao local ainda pode ser encerrada.
    } finally {
      removerTokenAutenticacao()
      setSaindo(false)
      router.push("/login")
    }
  }

  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--usuario-dashboard">
        <div className="hero-copy hero-copy--dashboard hero-copy--centered">
          <p className="eyebrow">Página do usuário</p>
          <h1 className="hero-title--centered">Gerenciador de carreira</h1>
          <p className="hero-subtitle hero-subtitle--dashboard">Career manager</p>
        </div>
      </section>

      <section className="workbench workbench--single">
        <section className="card results-card">
          <div className="tab-bar">
            <button
              className={abaAtiva === "perfil" ? "tab-button tab-button--active" : "tab-button"}
              type="button"
              onClick={() => setAbaAtiva("perfil")}
            >
              Perfil
            </button>
            <button
              className={
                abaAtiva === "historico" ? "tab-button tab-button--active" : "tab-button"
              }
              type="button"
              onClick={() => setAbaAtiva("historico")}
            >
              Histórico funcional
            </button>
          </div>

          {abaAtiva === "perfil" ? (
            <>
              <div className="card-header">
                <div>
                  <p className="eyebrow">Dados salvos</p>
                  <h2>Perfil do usuário</h2>
                </div>
                <span className="status-pill">
                  {usuario?.email_confirmado ? "confirmado" : "pendente"}
                </span>
              </div>

              {carregando ? (
                <div className="empty-state">
                  <p>Carregando dados da sessão...</p>
                </div>
              ) : erro ? (
                <div className="empty-state">
                  <p>{erro}</p>
                  <button
                    className="primary-button"
                    type="button"
                    onClick={() => void recarregarUsuario()}
                  >
                    Tentar novamente
                  </button>
                </div>
              ) : usuario ? (
                <>
                  <div className="results-grid">
                    <div className="result-block">
                      <span className="label">Nome completo</span>
                      <strong>{usuario.nome}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Apelido</span>
                      <strong>{usuario.apelido || "Não informado"}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">E-mail</span>
                      <strong>{usuario.email}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Data de exercício</span>
                      <strong>{formatarDataCurta(usuario.data_exercicio)}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Criado em</span>
                      <strong>{formatarData(usuario.criado_em)}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Confirmado em</span>
                      <strong>{formatarData(usuario.confirmado_em)}</strong>
                    </div>
                  </div>

                  <div className="actions">
                    <p className="helper">
                      O e-mail de confirmação foi enviado para <strong>{usuario.email}</strong>.
                    </p>
                    <div className="actions-row">
                      <button
                        className="ghost-button"
                        type="button"
                        onClick={() => void excluirCadastro()}
                        disabled={removendo}
                      >
                        {removendo ? "Removendo..." : "Limpar último cadastro"}
                      </button>
                      <button
                        className="ghost-button"
                        type="button"
                        onClick={() => void sair()}
                        disabled={saindo}
                      >
                        {saindo ? "Saindo..." : "Sair"}
                      </button>
                    </div>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <p>
                    Nenhuma sessão ativa foi encontrada. Entre novamente para ver seus dados.
                  </p>
                  <Link className="primary-button" href="/login">
                    Ir para o login
                  </Link>
                </div>
              )}
            </>
          ) : (
            <HistoricoFuncionalView
              usuarioId={usuario?.id ?? null}
              historicoInicial={historicoInicial}
            />
          )}
        </section>
      </section>
    </main>
  )
}
