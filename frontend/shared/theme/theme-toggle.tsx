"use client"

import { useLayoutEffect, useState } from "react"

import { useLanguage } from "@/shared/i18n/language-provider"

type ThemeMode = "dark" | "light"

const STORAGE_KEY = "career-theme-mode"

function aplicarTema(tema: ThemeMode) {
  document.documentElement.dataset.theme = tema
  document.documentElement.style.colorScheme = tema
}

function temaInicial(): ThemeMode {
  if (typeof window === "undefined") {
    return "dark"
  }

  const salvo = window.localStorage.getItem(STORAGE_KEY)
  if (salvo === "light" || salvo === "dark") {
    return salvo
  }

  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark"
}

export function ThemeToggle() {
  const { texts } = useLanguage()
  const [tema, setTema] = useState<ThemeMode>(() => temaInicial())
  const [pronto, setPronto] = useState(false)

  useLayoutEffect(() => {
    aplicarTema(tema)
    const frame = window.requestAnimationFrame(() => setPronto(true))
    return () => window.cancelAnimationFrame(frame)
  }, [tema])

  function alternarTema() {
    setTema((atual) => {
      const proximo = atual === "dark" ? "light" : "dark"
      window.localStorage.setItem(STORAGE_KEY, proximo)
      aplicarTema(proximo)
      return proximo
    })
  }

  if (!pronto) {
    return null
  }

  return (
    <button
      className="theme-toggle"
      type="button"
      onClick={alternarTema}
      aria-label={tema === "dark" ? texts.theme.lightTitle : texts.theme.darkTitle}
      title={tema === "dark" ? texts.theme.lightTitle : texts.theme.darkTitle}
    >
      <span className="theme-toggle__label">{texts.theme.label}</span>
      <span className="theme-toggle__pill" aria-hidden="true">
        <span className="theme-toggle__dot" />
      </span>
      <span className="theme-toggle__state">
        {tema === "dark" ? texts.theme.darkState : texts.theme.lightState}
      </span>
    </button>
  )
}
