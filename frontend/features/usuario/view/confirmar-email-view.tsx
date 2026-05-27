"use client"

import Link from "next/link"
import { useEffect, useState } from "react"

import { ApiResponseError } from "@/shared/api/client"
import { confirmarEmailUsuario } from "@/features/auth/model/auth.repository"

type ConfirmarEmailViewProps = {
  token: string | null
}

type EstadoConfirmacao = "carregando" | "sucesso" | "token_invalido" | "token_ausente" | "erro"

export function ConfirmarEmailView({ token }: ConfirmarEmailViewProps) {
  const [estado, setEstado] = useState<EstadoConfirmacao>(token ? "carregando" : "token_ausente")

  useEffect(() => {
    let ativo = true

    async function confirmar() {
      if (!token) {
        if (ativo) {
          setEstado("token_ausente")
        }
        return
      }

      try {
        await confirmarEmailUsuario(token)
        if (ativo) {
          setEstado("sucesso")
        }
      } catch (erro) {
        if (!ativo) {
          return
        }

        if (erro instanceof ApiResponseError && erro.status === 404) {
          setEstado("token_invalido")
          return
        }

        setEstado("erro")
      }
    }

    void confirmar()

    return () => {
      ativo = false
    }
  }, [token])

  const conteudo = {
    carregando: {
      titulo: "Confirmando seu cadastro...",
      subtitulo: "Estamos validando o seu link de confirma\u00e7\u00e3o. Isso leva apenas alguns segundos.",
    },
    sucesso: {
      titulo: "Cadastro confirmado com sucesso",
      subtitulo: "Seu acesso foi validado. Agora voc\u00ea j\u00e1 pode entrar na sua conta.",
    },
    token_ausente: {
      titulo: "Link inv\u00e1lido ou incompleto.",
      subtitulo: "Abra novamente o email de confirma\u00e7\u00e3o para acessar o link completo.",
    },
    token_invalido: {
      titulo: "Este link expirou ou j\u00e1 foi utilizado.",
      subtitulo: "Se precisar, solicite um novo email de confirma\u00e7\u00e3o na tela de cadastro.",
    },
    erro: {
      titulo: "N\u00e3o foi poss\u00edvel confirmar agora. Tente novamente.",
      subtitulo: "Houve uma falha t\u00e9cnica ao validar seu cadastro. Tente mais tarde.",
    },
  }[estado]

  const acaoPrincipal =
    estado === "sucesso" ? (
      <Link className="primary-button button--large confirm-email-card__button" href="/usuario">
        Ir para a p\u00e1gina de usu\u00e1rio
      </Link>
    ) : (
      <Link className="primary-button button--large confirm-email-card__button" href="/login">
        Ir para o login
      </Link>
    )

  return (
    <main className="page-shell page-shell--confirm-email">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="card confirm-email-card" aria-live="polite">
        <p className="eyebrow confirm-email-card__brand">Career Flow</p>
        <h1 className="confirm-email-card__title">{conteudo.titulo}</h1>
        <p className="confirm-email-card__subtitle">{conteudo.subtitulo}</p>

        {estado === "carregando" ? (
          <div className="confirm-email-card__status">
            <span className="confirm-email-card__spinner" aria-hidden="true" />
            <span>Confirmando seu cadastro...</span>
          </div>
        ) : null}

        {estado === "sucesso" ? (
          <p className="confirm-email-card__success-note">
            Seu acesso foi liberado com seguran\u00e7a.
          </p>
        ) : null}

        {estado === "token_ausente" || estado === "token_invalido" || estado === "erro" ? (
          <p className="confirm-email-card__hint">
            {estado === "erro"
              ? "Se o problema continuar, tente abrir o link novamente a partir do email mais recente."
              : "Se precisar, solicite um novo email de confirma\u00e7\u00e3o na tela de cadastro."}
          </p>
        ) : null}

        <div className="confirm-email-card__actions">{acaoPrincipal}</div>
      </section>
    </main>
  )
}
