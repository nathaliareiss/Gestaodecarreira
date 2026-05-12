"use client"

import { createContext, useContext, useLayoutEffect, useMemo, useState, type ReactNode } from "react"

import {
  LOCALE_TEXTS,
  SITE_LANGUAGE_STORAGE_KEY,
  normalizarIdioma,
  serializarCookieIdioma,
  type SiteLanguage,
} from "./messages"

type LanguageContextValue = {
  language: SiteLanguage
  texts: (typeof LOCALE_TEXTS)[SiteLanguage]
  setLanguage: (language: SiteLanguage) => void
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

function aplicarIdioma(idioma: SiteLanguage) {
  document.documentElement.dataset.language = idioma
  document.documentElement.lang = idioma
  document.cookie = serializarCookieIdioma(idioma)

  try {
    window.localStorage.setItem(SITE_LANGUAGE_STORAGE_KEY, idioma)
  } catch {
    // Ignora navegadores com storage indisponível.
  }
}

function idiomaInicial(idiomaInicial: SiteLanguage): SiteLanguage {
  if (typeof window === "undefined") {
    return idiomaInicial
  }

  try {
    const salvo = window.localStorage.getItem(SITE_LANGUAGE_STORAGE_KEY)
    if (salvo) {
      return normalizarIdioma(salvo)
    }
  } catch {
    // Se o storage falhar, seguimos com o idioma inicial vindo do servidor.
  }

  return idiomaInicial
}

type LanguageProviderProps = {
  initialLanguage: SiteLanguage
  children: ReactNode
}

export function LanguageProvider({ initialLanguage, children }: LanguageProviderProps) {
  const [language, setLanguageState] = useState<SiteLanguage>(() => idiomaInicial(initialLanguage))

  useLayoutEffect(() => {
    aplicarIdioma(language)
  }, [language])

  const value = useMemo<LanguageContextValue>(
    () => ({
      language,
      texts: LOCALE_TEXTS[language],
      setLanguage: setLanguageState,
    }),
    [language],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage() {
  const context = useContext(LanguageContext)

  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider.")
  }

  return context
}

export function removerCookieIdioma() {
  document.cookie = `${SITE_LANGUAGE_COOKIE_NAME}=; Path=/; Max-Age=0; SameSite=Lax`
}
