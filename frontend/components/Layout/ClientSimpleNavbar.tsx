'use client'

import { useEffect, useState } from 'react'
import SimpleNavbar from './SimpleNavbar'

export default function ClientSimpleNavbar() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <nav className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md shadow-xl border-b border-white/20 dark:border-gray-700/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-lg">CF</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-gray-900 to-purple-600 dark:from-white dark:to-purple-400 bg-clip-text text-transparent ml-3">
                CareerFinance AI
              </span>
            </div>
          </div>
        </div>
      </nav>
    )
  }

  return <SimpleNavbar />
}
