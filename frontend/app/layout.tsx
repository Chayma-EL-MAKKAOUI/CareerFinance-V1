import './globals.css'
import { Inter } from 'next/font/google'
import { ReactNode } from 'react'
<<<<<<< HEAD
import SimpleNavbar from '../components/Layout/SimpleNavbar'
import FloatingChatbot from '../components/Chat/FloatingChatbot'
import { ThemeProvider } from '../contexts/ThemeContext'
import ThemeToggle from '../components/ThemeToggle'
=======
import ClientSimpleNavbar from '../components/Layout/ClientSimpleNavbar'
import ClientFloatingChatbot from '../components/Chat/ClientFloatingChatbot'
import ThemeProvider from '../components/ThemeProvider'
import ClientThemeToggle from '../components/ClientThemeToggle'
>>>>>>> 5e0de77 (Auth commit)

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'CareerFinance AI',
  description: 'Votre assistant intelligent pour optimiser votre carrière et comprendre vos finances',
}

interface RootLayoutProps {
  children: ReactNode
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="fr">
      <body className={`${inter.className} antialiased`}>
        <ThemeProvider>
<<<<<<< HEAD
          <SimpleNavbar />
          {children}
          <FloatingChatbot />
          <ThemeToggle />
=======
          <ClientSimpleNavbar />
          {children}
          <ClientFloatingChatbot />
          <ClientThemeToggle />
>>>>>>> 5e0de77 (Auth commit)
        </ThemeProvider>
      </body>
    </html>
  )
}

