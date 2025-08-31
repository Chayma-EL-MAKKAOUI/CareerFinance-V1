"use client"

<<<<<<< HEAD
import FileUploader from '../../components/FileUploader'
import { useState } from 'react'

import Layout from '../../components/Layout/Layout'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/UI/Card'
import Button from '../../components/UI/Button'
=======
import FileUploader from '../../components/BulletinPaie/FileUploader'
import { useState } from 'react'
import AuthGuard from '../../components/Auth/AuthGuard'

import Layout from '../../components/Layout/Layout'
import { Card, CardHeader, CardTitle, CardContent } from '../../components/UI/Card'
import Button from '../../components/UI/button'
>>>>>>> 5e0de77 (Auth commit)

export default function BulletinPaiePage() {
  const [resultData, setResultData] = useState(null)
const [message, setMessage] = useState('')
const [uploading, setUploading] = useState(false)

const handleFileChange = async (file) => {
  const formData = new FormData()
  formData.append('file', file)

  setUploading(true)

  try {
    const response = await fetch('http://localhost:8000/api/documents/upload', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
<<<<<<< HEAD
      throw new Error('Erreur lors de l’envoi du fichier')
=======
      throw new Error('Erreur lors de l\'envoi du fichier')
>>>>>>> 5e0de77 (Auth commit)
    }

    const data = await response.json()
    setResultData(data)
    setMessage('Analyse terminée ✅')
  } catch (error) {
    setMessage('Erreur : ' + error.message)
  } finally {
    setUploading(false)
  }
}

  return (
<<<<<<< HEAD
    <Layout>
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <span className="text-6xl">📄</span>
          <h1 className="text-3xl font-bold text-gray-900 mb-2 mt-4">
            Analyse de Bulletin de Paie
          </h1>
          <p className="text-lg text-gray-600">
            Téléchargez votre bulletin de paie pour obtenir une analyse détaillée automatique
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <CardTitle>Télécharger votre bulletin</CardTitle>
            </CardHeader>
            <CardContent>
              <FileUploader onFileSelect={handleFileChange} />

              <Button className="w-full mt-6">
                Analyser mon bulletin
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Résultats de l'analyse</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <span className="text-4xl mb-4 block">📊</span>
                <p className="text-gray-500">
                  Aucune analyse disponible. Téléchargez un bulletin pour commencer.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
=======
    <AuthGuard>
      <Layout>
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <span className="text-6xl">📄</span>
            <h1 className="text-3xl font-bold text-gray-900 mb-2 mt-4">
              Analyse de Bulletin de Paie
            </h1>
            <p className="text-lg text-gray-600">
              Téléchargez votre bulletin de paie pour obtenir une analyse détaillée automatique
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card>
              <CardHeader>
                <CardTitle>Télécharger votre bulletin</CardTitle>
              </CardHeader>
              <CardContent>
                <FileUploader onFileSelect={handleFileChange} />

                <Button className="w-full mt-6">
                  Analyser mon bulletin
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Résultats de l'analyse</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <span className="text-4xl mb-4 block">📊</span>
                  <p className="text-gray-500">
                    Aucune analyse disponible. Téléchargez un bulletin pour commencer.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </Layout>
    </AuthGuard>
>>>>>>> 5e0de77 (Auth commit)
  )
}
