"use client"

import { useLayoutEffect, useState } from "react"

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
  const [tema, setTema] = useState<ThemeMode>("dark")
  const [pronto, setPronto] = useState(false)

  useLayoutEffect(() => {
    const inicial = temaInicial()
    setTema(inicial)
    aplicarTema(inicial)
    setPronto(true)
  }, [])

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
      aria-label={tema === "dark" ? "Ativar tema claro" : "Ativar tema escuro"}
      title={tema === "dark" ? "Ativar tema claro" : "Ativar tema escuro"}
    >
      <span className="theme-toggle__label">Tema</span>
      <span className="theme-toggle__pill" aria-hidden="true">
        <span className="theme-toggle__dot" />
      </span>
      <span className="theme-toggle__state">{tema === "dark" ? "Escuro" : "Claro"}</span>
    </button>
  )
}
