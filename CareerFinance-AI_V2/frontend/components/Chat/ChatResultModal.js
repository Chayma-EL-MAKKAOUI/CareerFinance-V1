'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../UI/Card';
import Button from '../UI/Button';
import ActionButtons from '../UI/ActionButtons';

const ChatResultModal = ({ 
  messages, 
  isOpen, 
  onClose 
}) => {
  const [chatContent, setChatContent] = useState('');

  useEffect(() => {
    if (messages && messages.length > 0) {
      const formattedContent = messages.map(msg => {
        const timestamp = msg.timestamp.toLocaleString('fr-FR');
        const sender = msg.sender === 'user' ? '👤 Vous' : '🤖 Assistant';
        return `[${timestamp}] ${sender}:\n${msg.text}\n`;
      }).join('\n---\n\n');
      
      setChatContent(formattedContent);
    }
  }, [messages]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <CardTitle>💬 Historique de la conversation</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-md whitespace-pre-line text-sm max-h-96 overflow-y-auto">
              {chatContent}
            </div>

            <ActionButtons
              content={chatContent}
              filename="conversation-chat.txt"
              title="Conversation avec l'assistant"
              showEdit={false}
              showSave={false}
            />
          </div>
        </CardContent>
      </div>
    </div>
  );
};

export default ChatResultModal;
