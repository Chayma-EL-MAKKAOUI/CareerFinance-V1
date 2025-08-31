'use client'

import { useEffect, useState } from 'react'
import { ThemeProvider as OriginalThemeProvider } from '../contexts/ThemeContext'

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return <>{children}</>
  }

  return <OriginalThemeProvider>{children}</OriginalThemeProvider>
}
