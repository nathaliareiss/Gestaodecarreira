import type { Metadata } from "next"
import type { ReactNode } from "react"

import "./globals.css"
import { ThemeToggle } from "@/shared/theme/theme-toggle"

export const metadata: Metadata = {
  title: "Career Progression Analyzer",
  description: "Cadastro, login, recuperação de senha e perfil funcional.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
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
            `,
          }}
        />
      </head>
      <body className="antialiased">
        <ThemeToggle />
        {children}
      </body>
    </html>
  )
}
