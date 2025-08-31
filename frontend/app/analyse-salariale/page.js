import Layout from '../../components/Layout/Layout'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/UI/Card'
import Button from '../../components/UI/Button'

export default function AnalyseSalarialePage() {
  return (
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <span className="text-6xl">📊</span>
          <h1 className="text-3xl font-bold text-gray-900 mb-2 mt-4">
            Analyse Salariale
          </h1>
          <p className="text-lg text-gray-600">
            Comparez votre salaire au marché et découvrez votre positionnement
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Informations sur votre poste</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Intitulé du poste
                </label>
                <input 
                  type="text" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Développeur Full Stack"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Années d'expérience
                </label>
                <input 
                  type="number" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: 3"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Localisation
                </label>
                <input 
                  type="text" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Casablanca"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Salaire actuel (MAD/mois)
                </label>
                <input 
                  type="number" 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: 15000"
                />
              </div>
            </div>
            
            <Button className="w-full mt-6">
              Analyser mon positionnement
            </Button>
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}