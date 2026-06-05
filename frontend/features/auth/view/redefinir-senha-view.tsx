"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useEffect, useMemo, useState, type FormEvent } from "react"

import { ApiResponseError } from "@/shared/api/client"
import { useLanguage } from "@/shared/i18n/language-provider"
import { redefinirSenhaUsuario } from "../model/auth.repository"

type RedefinirSenhaViewProps = {
  token: string | null
}

type EstadoTela = "formulario" | "sucesso" | "token_ausente" | "token_invalido" | "erro"

function obterTextos(language: "pt-BR" | "en") {
  if (language === "en") {
    return {
      eyebrow: "Reset Password",
      title: "Create a new password to access your account.",
      subtitle: "Use the link you received by email to set a new password securely.",
      formTitle: "Update Access",
      newPassword: "New Password",
      confirmPassword: "Confirm Password",
      submit: "Reset Password",
      submitting: "Updating...",
      backToLogin: "Back to Sign In",
      missingTokenTitle: "Link missing or incomplete.",
      missingTokenSubtitle: "Open the most recent email or request a new password reset link.",
      invalidTokenTitle: "This link expired or was already used.",
      invalidTokenSubtitle: "Request a new link to restart the password reset flow.",
      genericErrorTitle: "We couldn't update the password right now.",
      genericErrorSubtitle: "Please try again in a moment.",
      successTitle: "Password updated successfully.",
      successSubtitle: "You can now sign in with your new password.",
      requestNewLink: "Request a new link",
      requestNewLinkHref: "/login?modo=recuperacao",
    }
  }

  return {
    eyebrow: "Redefinir senha",
    title: "Crie uma nova senha para acessar sua conta.",
    subtitle: "Use o link recebido por e-mail para definir uma nova senha com segurança.",
    formTitle: "Atualizar acesso",
    newPassword: "Nova senha",
    confirmPassword: "Confirmar senha",
    submit: "Redefinir senha",
    submitting: "Atualizando...",
    backToLogin: "Voltar ao login",
    missingTokenTitle: "Link inválido ou incompleto.",
    missingTokenSubtitle: "Abra o e-mail mais recente ou solicite um novo link de redefinição.",
    invalidTokenTitle: "Este link expirou ou já foi usado.",
    invalidTokenSubtitle: "Solicite um novo link para reiniciar o fluxo de redefinição.",
    genericErrorTitle: "Não foi possível atualizar a senha agora.",
    genericErrorSubtitle: "Tente novamente em instantes.",
    successTitle: "Senha atualizada com sucesso.",
    successSubtitle: "Agora você pode entrar com a nova senha.",
    requestNewLink: "Solicitar novo link",
    requestNewLinkHref: "/login?modo=recuperacao",
  }
}

export function RedefinirSenhaView({ token }: RedefinirSenhaViewProps) {
  const router = useRouter()
  const { language } = useLanguage()
  const textos = useMemo(() => obterTextos(language), [language])
  const [novaSenha, setNovaSenha] = useState("")
  const [confirmarSenha, setConfirmarSenha] = useState("")
  const [carregando, setCarregando] = useState(false)
  const [estado, setEstado] = useState<EstadoTela>(token ? "formulario" : "token_ausente")
  const [mensagemErro, setMensagemErro] = useState<string | null>(null)

  useEffect(() => {
    setEstado(token ? "formulario" : "token_ausente")
    setMensagemErro(null)
  }, [token])

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    setMensagemErro(null)

    if (!token) {
      setEstado("token_ausente")
      return
    }

    if (novaSenha !== confirmarSenha) {
      setMensagemErro(language === "en" ? "Passwords do not match." : "As senhas não coincidem.")
      return
    }

    setCarregando(true)

    try {
      const resposta = await redefinirSenhaUsuario({
        token,
        nova_senha: novaSenha,
      })

      setEstado("sucesso")
      setNovaSenha("")
      setConfirmarSenha("")
      setMensagemErro(resposta.message)

      window.setTimeout(() => {
        router.push("/login")
      }, 1200)
    } catch (error) {
      if (error instanceof ApiResponseError && error.status === 404) {
        setEstado("token_invalido")
        return
      }

      setEstado("erro")
      setMensagemErro(error instanceof Error ? error.message : null)
    } finally {
      setCarregando(false)
    }
  }

  const estadoMensagem = {
    formulario: {
      titulo: textos.title,
      subtitulo: textos.subtitle,
      banner: null,
    },
    sucesso: {
      titulo: textos.successTitle,
      subtitulo: textos.successSubtitle,
      banner: textos.successTitle,
    },
    token_ausente: {
      titulo: textos.missingTokenTitle,
      subtitulo: textos.missingTokenSubtitle,
      banner: textos.missingTokenTitle,
    },
    token_invalido: {
      titulo: textos.invalidTokenTitle,
      subtitulo: textos.invalidTokenSubtitle,
      banner: textos.invalidTokenTitle,
    },
    erro: {
      titulo: textos.genericErrorTitle,
      subtitulo: textos.genericErrorSubtitle,
      banner: textos.genericErrorTitle,
    },
  }[estado]

  const mostrarFormulario = estado === "formulario"

  return (
    <main className="page-shell">
      <div className="bg-orb bg-orb-a" />
      <div className="bg-orb bg-orb-b" />

      <section className="hero hero--login">
        <div className="hero-copy hero-copy--login">
          <p className="eyebrow">{textos.eyebrow}</p>
          <h1>{estadoMensagem.titulo}</h1>
          <p className="hero-text">{estadoMensagem.subtitulo}</p>
        </div>

        <div className="login-panel">
          <form className="card form-card form-card--recovery" onSubmit={enviar}>
            <div className="card-header card-header--tight">
              <div>
                <p className="eyebrow">{estadoMensagem.banner ?? textos.eyebrow}</p>
                <h2>{textos.formTitle}</h2>
              </div>
            </div>

            {mostrarFormulario ? (
              <>
                <label className="field">
                  <span>{textos.newPassword}</span>
                  <input
                    type="password"
                    value={novaSenha}
                    onChange={(evento) => setNovaSenha(evento.target.value)}
                    placeholder="********"
                    autoComplete="new-password"
                    minLength={6}
                    required
                  />
                </label>

                <label className="field">
                  <span>{textos.confirmPassword}</span>
                  <input
                    type="password"
                    value={confirmarSenha}
                    onChange={(evento) => setConfirmarSenha(evento.target.value)}
                    placeholder="********"
                    autoComplete="new-password"
                    minLength={6}
                    required
                  />
                </label>
              </>
            ) : null}

            {mensagemErro ? <p className={estado === "sucesso" ? "success-box" : "error-box"}>{mensagemErro}</p> : null}

            {mostrarFormulario ? (
              <div className="actions actions--compact">
                <button className="primary-button button--large" type="submit" disabled={carregando}>
                  {carregando ? textos.submitting : textos.submit}
                </button>
                <Link className="ghost-button ghost-button--compact" href="/login">
                  {textos.backToLogin}
                </Link>
              </div>
            ) : (
              <div className="actions actions--compact">
                <Link className="primary-button button--large" href={textos.requestNewLinkHref}>
                  {textos.requestNewLink}
                </Link>
                <Link className="ghost-button ghost-button--compact" href="/login">
                  {textos.backToLogin}
                </Link>
              </div>
            )}
          </form>
        </div>
      </section>
    </main>
  )
}
