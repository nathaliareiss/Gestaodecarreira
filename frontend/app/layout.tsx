import type { Metadata } from "next"
import type { ReactNode } from "react"

import "./globals.css"
import { ThemeToggle } from "@/shared/theme/theme-toggle"

export const metadata: Metadata = {
  title: "Career Management | Career Progression Analyzer",
  description: "Sign up, login, password recovery, and career history in one place.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        <ThemeToggle />
        {children}
      </body>
    </html>
  )
}
