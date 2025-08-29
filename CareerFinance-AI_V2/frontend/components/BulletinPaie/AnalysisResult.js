'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../UI/Card';
import Button from '../UI/Button';
import ActionButtons from '../UI/ActionButtons';
import ProtectedModal from '../UI/ProtectedModal';

const AnalysisResult = ({ result, isOpen, onClose, onSave }) => {
  const [editedResult, setEditedResult] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (result) {
      setEditedResult(typeof result === 'string' ? result : JSON.stringify(result, null, 2));
    }
  }, [result]);

  const handleSave = () => {
    if (onSave) {
      onSave(editedResult);
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
              <CardTitle>Analyse du bulletin de paie</CardTitle>
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
                    Modifier l'analyse
                  </label>
                  <textarea
                    value={editedResult}
                    onChange={(e) => setEditedResult(e.target.value)}
                    className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    placeholder="Entrez votre analyse..."
                    autoFocus
                  />
                </div>
              ) : (
                <div>
                  <div className="bg-gray-50 p-4 rounded-md whitespace-pre-line">
                    {editedResult}
                  </div>
                </div>
              )}

              <ActionButtons
                content={editedResult}
                filename="analyse-bulletin-paie.txt"
                title="Analyse bulletin de paie"
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

export default AnalysisResult; 