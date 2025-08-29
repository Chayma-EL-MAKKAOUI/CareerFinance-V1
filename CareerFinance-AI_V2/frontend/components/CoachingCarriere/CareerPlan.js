'use client';
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../UI/Card';
import Button from '../UI/Button';
import ActionButtons from '../UI/ActionButtons';
import ProtectedModal from '../UI/ProtectedModal';

const CareerPlan = ({ plan, isOpen, onClose, onSave }) => {
  const [editedPlan, setEditedPlan] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (plan) {
      setEditedPlan(typeof plan === 'string' ? plan : JSON.stringify(plan, null, 2));
    }
  }, [plan]);

  const handleSave = () => {
    if (onSave) {
      onSave(editedPlan);
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
              <CardTitle>Plan de carrière</CardTitle>
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
                    Modifier le plan
                  </label>
                  <textarea
                    value={editedPlan}
                    onChange={(e) => setEditedPlan(e.target.value)}
                    className="w-full h-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                    placeholder="Entrez votre plan de carrière..."
                    autoFocus
                  />
                </div>
              ) : (
                <div>
                  <div className="bg-gray-50 p-4 rounded-md whitespace-pre-line">
                    {editedPlan}
                  </div>
                </div>
              )}

              <ActionButtons
                content={editedPlan}
                filename="plan-carriere.txt"
                title="Plan de carrière"
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

export default CareerPlan; 