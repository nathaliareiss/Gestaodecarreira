"use client"

import Link from "next/link"
import { useState } from "react"

import { type UsuarioConta } from "@/features/usuario/model/usuario.model"
import {
  buscarUsuarioMaisRecente,
  removerUsuarioMaisRecente,
} from "@/features/usuario/model/usuario.repository"
import type { HistoricoFuncionalAnalise } from "@/features/historico-funcional/model/historico-funcional.model"
import { HistoricoFuncionalView } from "@/features/historico-funcional/view/historico-funcional-view"

function formatarData(valor: string | null) {
  if (!valor) {
    return "-"
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "medium",
    timeStyle: "short",
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
  const [usuario, setUsuario] = useState<UsuarioConta | null>(usuarioInicial)
  const [abaAtiva, setAbaAtiva] = useState<"perfil" | "historico">("perfil")
  const [erro, setErro] = useState<string | null>(erroInicial)
  const [carregando, setCarregando] = useState(false)
  const [removendo, setRemovendo] = useState(false)

  async function recarregarUsuario() {
    setCarregando(true)
    setErro(null)

    try {
      const dados = await buscarUsuarioMaisRecente()
      setUsuario(dados)
    } catch (error) {
      setErro(error instanceof Error ? error.message : "Falha inesperada ao carregar")
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
      setErro(error instanceof Error ? error.message : "Falha inesperada ao remover")
    } finally {
      setRemovendo(false)
    }
  }

  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Pagina do usuario</p>
          <h1>Os dados agora vem da API, nao do navegador.</h1>
          <p className="hero-text">
            Esta pagina carrega o cadastro mais recente salvo no banco e acompanha o
            estado de confirmacao do email.
          </p>
        </div>

        <div className="hero-grid">
          <article className="mini-card">
            <h2>Status</h2>
            <p>{usuario ? "Cadastro encontrado" : "Nenhum cadastro salvo"}</p>
          </article>
          <article className="mini-card">
            <h2>Email</h2>
            <p>{usuario ? usuario.email : "Aguardando novo cadastro"}</p>
          </article>
          <article className="mini-card">
            <h2>Confirmacao</h2>
            <p>{usuario?.email_confirmado ? "Confirmado" : "Pendente"}</p>
          </article>
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
              Historico funcional
            </button>
          </div>

          {abaAtiva === "perfil" ? (
            <>
              <div className="card-header">
                <div>
                  <p className="eyebrow">Dados salvos</p>
                  <h2>Perfil do usuario</h2>
                </div>
                <span className="status-pill">
                  {usuario?.email_confirmado ? "confirmado" : "pendente"}
                </span>
              </div>

              {carregando ? (
                <div className="empty-state">
                  <p>Carregando dados do usuario...</p>
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
                      <span className="label">Nome exibido</span>
                      <strong>{usuario.apelido || usuario.nome}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Nome completo</span>
                      <strong>{usuario.nome}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Apelido</span>
                      <strong>{usuario.apelido || "Nao informado"}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Email</span>
                      <strong>{usuario.email}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Login</span>
                      <strong>{usuario.login}</strong>
                    </div>
                    <div className="result-block">
                      <span className="label">Senha</span>
                      <strong>{usuario.senha_cadastrada ? "Cadastrada" : "-"}</strong>
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
                      O email de confirmação foi enviado para{" "}
                      <strong>{usuario.email}</strong>.
                    </p>
                    <button
                      className="ghost-button"
                      type="button"
                      onClick={() => void excluirCadastro()}
                      disabled={removendo}
                    >
                      {removendo ? "Removendo..." : "Limpar cadastro salvo"}
                    </button>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <p>
                    Ainda nao existe nenhum usuario salvo. Volte para o cadastro e crie uma
                    conta para ver os dados aqui.
                  </p>
                  <Link className="primary-button" href="/">
                    Ir para o cadastro
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
