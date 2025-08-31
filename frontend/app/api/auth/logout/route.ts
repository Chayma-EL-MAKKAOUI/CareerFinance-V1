import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002'

export async function POST(request: NextRequest) {
  try {
    console.log('📡 API Route - Tentative de déconnexion')
    
    // Rediriger vers le backend
    const response = await fetch(`${BACKEND_URL}/api/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    const data = await response.json()
    
    console.log('📡 API Route - Réponse du backend:', data)
    
    return NextResponse.json(data, { status: response.status })
  } catch (error) {
    console.error('❌ API Route - Erreur:', error)
    return NextResponse.json(
      { success: false, error: 'Erreur interne du serveur' },
      { status: 500 }
    )
  }
}
