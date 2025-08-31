'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../UI/Card';
<<<<<<< HEAD
import Button from '../UI/Button';
=======
import Button from '../UI/button';
>>>>>>> 5e0de77 (Auth commit)
import ActionButtons from '../UI/ActionButtons';

const AIResponse = ({ response, isOpen, onClose, onSave }) => {
  const [editedResponse, setEditedResponse] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (response) {
      setEditedResponse(typeof response === 'string' ? response : JSON.stringify(response, null, 2));
    }
  }, [response]);

  const handleSave = () => {
    if (onSave) {
      onSave(editedResponse);
    }
    setIsEditing(false);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <CardHeader className="border-b">
          <div className="flex items-center justify-between">
            <CardTitle>🤖 Réponse de l'IA</CardTitle>
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
            {isEditing ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Modifier la réponse
                </label>
                <textarea
                  value={editedResponse}
                  onChange={(e) => setEditedResponse(e.target.value)}
                  className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  placeholder="Entrez la réponse de l'IA..."
                  autoFocus
                />
              </div>
            ) : (
              <div>
                <div className="bg-blue-50 p-4 rounded-md whitespace-pre-line border-l-4 border-blue-500">
                  {editedResponse}
                </div>
              </div>
            )}

            <ActionButtons
              content={editedResponse}
              filename="reponse-ai.txt"
              title="Réponse de l'IA"
              showEdit={!isEditing}
              onEdit={handleEdit}
              showSave={isEditing}
              onSave={handleSave}
            />
          </div>
        </CardContent>
      </div>
    </div>
  );
};

export default AIResponse; 