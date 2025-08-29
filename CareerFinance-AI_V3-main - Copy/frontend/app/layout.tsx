import './globals.css'
import { Inter } from 'next/font/google'
import { ReactNode } from 'react'
import SimpleNavbar from '../components/Layout/SimpleNavbar'
import FloatingChatbot from '../components/Chat/FloatingChatbot'
import { ThemeProvider } from '../contexts/ThemeContext'
import ThemeToggle from '../components/ThemeToggle'

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
          <SimpleNavbar />
          {children}
          <FloatingChatbot />
          <ThemeToggle />
        </ThemeProvider>
      </body>
    </html>
  )
}

