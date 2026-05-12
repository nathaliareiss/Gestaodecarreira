import type { Metadata } from "next"
import { cookies } from "next/headers"
import type { ReactNode } from "react"

import "./globals.css"
import { ThemeToggle } from "@/shared/theme/theme-toggle"
import { LanguageProvider } from "@/shared/i18n/language-provider"
import { LanguageToggle } from "@/shared/i18n/language-toggle"
import { normalizarIdioma, SITE_LANGUAGE_COOKIE_NAME } from "@/shared/i18n/messages"

export const metadata: Metadata = {
  title: "Career Management | Career Progression Analyzer",
  description: "Sign up, login, password recovery, and career history in one place.",
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: ReactNode
}>) {
  const cookieStore = await cookies()
  const idiomaInicial = normalizarIdioma(cookieStore.get(SITE_LANGUAGE_COOKIE_NAME)?.value)

  return (
    <html lang={idiomaInicial} suppressHydrationWarning>
      <body className="antialiased">
        <LanguageProvider initialLanguage={idiomaInicial}>
          <div className="top-controls" aria-label="Site controls">
            <ThemeToggle />
            <LanguageToggle />
          </div>
          {children}
        </LanguageProvider>
      </body>
    </html>
  )
}
