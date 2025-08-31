'use client'

import { useEffect, useState } from 'react'
import ThemeToggle from './ThemeToggle'

export default function ClientThemeToggle() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return <ThemeToggle />
}
