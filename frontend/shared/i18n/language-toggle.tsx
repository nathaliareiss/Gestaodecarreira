"use client"

import { useLayoutEffect, useState } from "react"

import { useLanguage } from "./language-provider"

export function LanguageToggle() {
  const { language, texts, setLanguage } = useLanguage()
  const [pronto, setPronto] = useState(false)

  useLayoutEffect(() => {
    const frame = window.requestAnimationFrame(() => setPronto(true))
    return () => window.cancelAnimationFrame(frame)
  }, [])

  function alternarIdioma() {
    setLanguage(language === "pt-BR" ? "en" : "pt-BR")
  }

  if (!pronto) {
    return null
  }

  const estaEmPortugues = language === "pt-BR"

  return (
    <button
      className="language-toggle"
      type="button"
      onClick={alternarIdioma}
      aria-label={estaEmPortugues ? texts.language.ptTitle : texts.language.enTitle}
      title={estaEmPortugues ? texts.language.ptTitle : texts.language.enTitle}
    >
      <span className="language-toggle__label">{texts.language.label}</span>
      <span className="language-toggle__pill" aria-hidden="true">
        <span className="language-toggle__dot" />
      </span>
      <span className="language-toggle__state">
        {estaEmPortugues ? texts.language.ptState : texts.language.enState}
      </span>
    </button>
  )
}
