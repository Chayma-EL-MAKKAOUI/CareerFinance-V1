'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../UI/Card';
import Button from '../UI/Button';
import ActionButtons from '../UI/ActionButtons';
import ProtectedModal from '../UI/ProtectedModal';

const NegotiationScript = ({ script, isOpen, onClose, onSave }) => {
  const [editedScript, setEditedScript] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (script) {
      setEditedScript(script);
    }
  }, [script]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSave();
    }
  };

  const handleSave = () => {
    if (onSave) {
      onSave(editedScript);
    }
    setIsEditing(false);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  if (!isOpen) return null;

  return (
    <ProtectedModal isOpen={isOpen} onClose={onClose}>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
          <CardHeader className="border-b">
            <div className="flex items-center justify-between">
              <CardTitle>Script de négociation</CardTitle>
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
                    Modifier le script
                  </label>
                  <textarea
                    value={editedScript}
                    onChange={(e) => setEditedScript(e.target.value)}
                    onKeyDown={handleKeyPress}
                    className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    placeholder="Entrez votre script de négociation..."
                    autoFocus
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    Appuyez sur Ctrl+Entrée (ou Cmd+Entrée sur Mac) pour sauvegarder
                  </div>
                </div>
              ) : (
                <div>
                  <div className="bg-gray-50 p-4 rounded-md whitespace-pre-line">
                    {editedScript}
                  </div>
                </div>
              )}

              <ActionButtons
                content={editedScript}
                filename="script-negociation.txt"
                title="Script de négociation"
                showEdit={!isEditing}
                onEdit={handleEdit}
                showSave={isEditing}
                onSave={handleSave}
              />
            </div>
          </CardContent>
        </div>
      </div>
    </ProtectedModal>
  );
};

export default NegotiationScript; 