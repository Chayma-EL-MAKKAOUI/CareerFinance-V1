'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './Card';
import Button from './Button';
import ActionButtons from './ActionButtons';

const ResultModal = ({ 
  title, 
  content, 
  isOpen, 
  onClose, 
  onSave,
  filename = 'resultat.txt',
  showEdit = true,
  showSave = true
}) => {
  const [editedContent, setEditedContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (content) {
      setEditedContent(typeof content === 'string' ? content : JSON.stringify(content, null, 2));
    }
  }, [content]);

  const handleSave = () => {
    if (onSave) {
      onSave(editedContent);
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
            <CardTitle>{title}</CardTitle>
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
                  Modifier le contenu
                </label>
                <textarea
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  placeholder="Entrez votre contenu..."
                  autoFocus
                />
              </div>
            ) : (
              <div>
                <div className="bg-gray-50 p-4 rounded-md whitespace-pre-line">
                  {editedContent}
                </div>
              </div>
            )}

            <ActionButtons
              content={editedContent}
              filename={filename}
              title={title}
              showEdit={showEdit && !isEditing}
              onEdit={handleEdit}
              showSave={showSave && isEditing}
              onSave={handleSave}
            />
          </div>
        </CardContent>
      </div>
    </div>
  );
};

export default ResultModal;
