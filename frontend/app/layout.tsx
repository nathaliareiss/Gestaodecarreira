import type { Metadata } from "next"
import type { ReactNode } from "react"

import "./globals.css"
import { ThemeToggle } from "@/shared/theme/theme-toggle"

export const metadata: Metadata = {
  title: "Gestão de Carreira | Career Progression Analyzer",
  description: "Cadastro, login, recuperação de senha e histórico funcional em um só lugar.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className="antialiased">
        <ThemeToggle />
        {children}
      </body>
    </html>
  )
}
