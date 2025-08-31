import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Routes publiques qui ne nécessitent pas d'authentification
const publicRoutes = [
  '/',
  '/login',
  '/register',
  '/auth/login',
  '/auth/register',
  '/api/auth',
  '/favicon.ico',
  '/_next',
  '/static'
]

// Routes protégées qui nécessitent une authentification
const protectedRoutes = [
  '/dashboard',
  '/dashboard-simple',
  '/documents',
  '/analyses',
  '/coaching',
  '/coaching-carriere',
  '/analyse-salariale',
  '/bulletin-paie',
  '/historique',
  '/test',
  '/test-auth',
  '/auth-test',
  '/auth-test-simple'
]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Vérifier si la route actuelle est publique
  const isPublicRoute = publicRoutes.some(route => 
    pathname === route || pathname.startsWith(route + '/')
  )
  
  // Vérifier si la route actuelle est protégée
  const isProtectedRoute = protectedRoutes.some(route => 
    pathname === route || pathname.startsWith(route + '/')
  )
  
  // Si c'est une route publique, permettre l'accès
  if (isPublicRoute) {
    return NextResponse.next()
  }
  
  // Si c'est une route protégée, vérifier l'authentification
  if (isProtectedRoute) {
    // Vérifier le token dans les cookies ou headers
    const token = request.cookies.get('auth_token')?.value || 
                  request.headers.get('authorization')?.replace('Bearer ', '')
    
    if (!token) {
      // Pas de token, rediriger vers la page de connexion
      const loginUrl = new URL('/auth/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }
    
    // Token présent, permettre l'accès
    return NextResponse.next()
  }
  
  // Pour toutes les autres routes, permettre l'accès
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
