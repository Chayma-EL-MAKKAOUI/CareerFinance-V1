'use client'

import { useEffect, useState } from 'react'
import FloatingChatbot from './FloatingChatbot'

export default function ClientFloatingChatbot() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return null
  }

  return <FloatingChatbot />
}
