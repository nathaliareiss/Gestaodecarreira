"use client"

import Link from "next/link"
import { useEffect, useState } from "react"

import type { UsuarioConta } from "@/features/usuario/model/usuario.model"
import {
  carregarUsuario,
  gerarLinkConfirmacao,
  limparUsuario,
} from "@/features/usuario/model/usuario.storage"

function formatarData(valor: string | null) {
  if (!valor) {
    return "-"
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(valor))
}

export default function UsuarioPage() {
  const [usuario, setUsuario] = useState<UsuarioConta | null>(null)
  const [carregando, setCarregando] = useState(true)

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setUsuario(carregarUsuario())
      setCarregando(false)
    }, 0)

    return () => window.clearTimeout(timer)
  }, [])

  const linkConfirmacao = usuario ? gerarLinkConfirmacao(usuario.token_confirmacao_email) : ""

  function excluirCadastro() {
    limparUsuario()
    setUsuario(null)
  }

  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Pagina do usuario</p>
          <h1>Os dados ficam aqui, nao mais na home.</h1>
          <p className="hero-text">
            Esta pagina mostra o cadastro salvo no navegador e acompanha o estado de
            confirmacao do email.
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

      <section className="workbench">
        <section className="card results-card">
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
                  <strong>{usuario.senha ? "Cadastrada" : "-"}</strong>
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
                  Link de confirmacao para este cadastro:
                  <br />
                  <code>{linkConfirmacao}</code>
                </p>
                <button className="ghost-button" type="button" onClick={excluirCadastro}>
                  Limpar cadastro local
                </button>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <p>
                Ainda nao existe nenhum usuario salvo neste navegador. Volte para o
                cadastro e crie uma conta para ver os dados aqui.
              </p>
              <Link className="primary-button" href="/">
                Ir para o cadastro
              </Link>
            </div>
          )}
        </section>

        <aside className="note-card">
          <p className="eyebrow">Sobre o email</p>
          <h2>API gratuita para confirmacao</h2>
          <p>
            Para o fluxo de confirmacao, duas opcoes gratuitas e praticas sao:
          </p>
          <ul>
            <li>
              <strong>Resend</strong>: plano free com 3.000 emails por mes e limite diario
              de 100 emails.
            </li>
            <li>
              <strong>Brevo</strong>: plano free com 300 emails por dia e envio de emails
              transacionais.
            </li>
          </ul>
          <p>
            Eu começaria por Resend se voce quer uma API simples para link de confirmacao.
          </p>
        </aside>
      </section>
    </main>
  )
}
