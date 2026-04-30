import type { Metadata } from "next"
import Script from "next/script"
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
      <head>
        <Script id="theme-bootstrap" strategy="beforeInteractive">
          {`
            (function() {
              try {
                var chave = 'career-theme-mode';
                var tema = localStorage.getItem(chave);
                if (tema !== 'light' && tema !== 'dark') {
                  tema = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
                }
                document.documentElement.dataset.theme = tema;
                document.documentElement.style.colorScheme = tema;
              } catch (error) {}
            })();
          `}
        </Script>
      </head>
      <body className="antialiased">
        <ThemeToggle />
        {children}
      </body>
    </html>
  )
}
