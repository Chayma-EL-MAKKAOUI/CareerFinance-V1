'use client'

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-8">Test Page</h1>
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl">
          <p className="text-lg text-gray-700">
            Cette page de test fonctionne correctement. Si vous voyez ceci, le problème n'est pas avec Next.js.
          </p>
          <div className="mt-6 space-y-4">
            <button className="bg-gradient-to-r from-purple-500 to-cyan-400 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all">
              Bouton de test
            </button>
            <div className="bg-blue-50 p-4 rounded-xl">
              <p className="text-blue-800">Zone de test avec styles</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
