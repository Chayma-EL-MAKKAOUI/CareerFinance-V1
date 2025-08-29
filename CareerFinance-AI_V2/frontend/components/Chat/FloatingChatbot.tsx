'use client'

import { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send, Minimize2, Maximize2, History } from 'lucide-react'
import ChatResultModal from './ChatResultModal'

interface Message {
  id: string
  text: string
  sender: 'user' | 'bot'
  timestamp: Date
}

export default function FloatingChatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: ' Bonjour ! Je suis votre assistant CareerFinance AI. Comment puis-je vous aider aujourd\'hui ?\n\nVous pouvez me poser des questions sur :\n• 📄 Analyse de bulletins de paie\n• 💰 Comparaison salariale\n• 🎯 Coaching carrière\n• 🤝 Navigation sur la plateforme',
      sender: 'bot',
      timestamp: new Date()
    }
  ])
  const [isTyping, setIsTyping] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!message.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: message,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setMessage('')
    setIsTyping(true)

    // Simulation de réponse du bot
    setTimeout(() => {
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: getBotResponse(message),
        sender: 'bot',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, botResponse])
      setIsTyping(false)

      // Effet sonore simulé (vibration sur mobile)
      if (navigator.vibrate) {
        navigator.vibrate(100)
      }
    }, 1500)
  }

  const getBotResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase()
    
    if (lowerMessage.includes('bulletin') || lowerMessage.includes('paie')) {
      return ' Pour analyser votre bulletin de paie, rendez-vous dans l\'onglet "Bulletin de Paie" sur la page d\'accueil. Vous pourrez y télécharger votre document et obtenir une analyse détaillée.'
    }
    
    if (lowerMessage.includes('salaire') || lowerMessage.includes('salarial')) {
      return ' L\'analyse salariale vous permet de comparer votre rémunération au marché. Utilisez l\'onglet "Analyse Salariale" pour saisir vos informations et découvrir votre positionnement.'
    }
    
    if (lowerMessage.includes('carrière') || lowerMessage.includes('coaching')) {
      return ' Notre service de coaching carrière vous aide à planifier votre évolution professionnelle. Consultez l\'onglet "Coaching Carrière" pour générer votre plan personnalisé.'
    }
    
    if (lowerMessage.includes('aide') || lowerMessage.includes('help')) {
      return ' Je peux vous aider avec :\n• Analyse de bulletins de paie\n• Comparaison salariale\n• Coaching carrière\n• Navigation sur la plateforme\n\nQue souhaitez-vous faire ?'
    }
    
    return ' Merci pour votre message ! Je suis là pour vous aider avec vos questions sur les bulletins de paie, l\'analyse salariale et le coaching carrière. Pouvez-vous me donner plus de détails sur ce que vous recherchez ?'
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="group relative w-16 h-16 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full shadow-2xl hover:shadow-purple-500/25 hover:scale-110 transition-all duration-300 flex items-center justify-center animate-pulse"
        >
          <MessageCircle className="w-8 h-8 text-white" />
          

          
          {/* Effet de pulsation */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-purple-500 to-cyan-400 animate-ping opacity-20"></div>
          
          {/* Tooltip */}
          <div className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
            Besoin d'aide ? 
            <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
          </div>
        </button>
      </div>
    )
  }

  return (
    <>
      <div className="fixed bottom-6 right-6 z-50">
        <div className={`bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 transition-all duration-300 ${
          isMinimized ? 'w-80 h-16' : 'w-96 h-[500px]'
        }`}>
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-purple-500 to-cyan-400 rounded-t-2xl">
            <div className="flex items-center space-x-3">
              <div>
                <h3 className="text-white font-semibold">Assistant CareerFinance</h3>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowHistory(true)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
                title="Voir l'historique"
              >
                <History className="w-4 h-4 text-white" />
              </button>
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                {isMinimized ? (
                  <Maximize2 className="w-4 h-4 text-white" />
                ) : (
                  <Minimize2 className="w-4 h-4 text-white" />
                )}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-4 h-4 text-white" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages */}
              <div className="flex-1 p-4 h-80 overflow-y-auto custom-scrollbar">
                <div className="space-y-4">
                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`px-4 py-2 rounded-2xl max-w-xs ${
                        msg.sender === 'user'
                          ? 'bg-gradient-to-r from-purple-500 to-cyan-400 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                      }`}>
                        <p className="text-sm whitespace-pre-line">{msg.text}</p>
                        <p className={`text-xs mt-1 ${
                          msg.sender === 'user' ? 'text-white/70' : 'text-gray-500 dark:text-gray-400'
                        }`}>
                          {msg.timestamp.toLocaleTimeString('fr-FR', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>
                  ))}
                  
                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 px-4 py-2 rounded-2xl max-w-xs">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>
              </div>

              {/* Suggestions rapides */}
              {messages.length === 1 && (
                <div className="px-4 pb-2">
                  <div className="flex flex-wrap gap-2">
                    {['Comment analyser mon bulletin ?', 'Comparer mon salaire', 'Conseils carrière'].map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => setMessage(suggestion)}
                        className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Input */}
              <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Tapez votre message..."
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!message.trim()}
                    className="px-4 py-2 bg-gradient-to-r from-purple-500 to-cyan-400 text-white rounded-xl hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Modal d'historique */}
      <ChatResultModal
        messages={messages}
        isOpen={showHistory}
        onClose={() => setShowHistory(false)}
      />
    </>
  )
}
