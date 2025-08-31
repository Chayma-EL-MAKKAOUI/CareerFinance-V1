'use client';
import React from 'react';
import Button from './Button';

const ActionButtons = ({ 
  content, 
  filename = 'document.txt', 
  title = 'Document',
  onDownload,
  onShare,
  className = '',
  showEdit = false,
  onEdit,
  showSave = false,
  onSave
}) => {
  const handleDownload = () => {
    if (onDownload) {
      onDownload();
      return;
    }

    const element = document.createElement('a');
    const file = new Blob([content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleShare = async () => {
    if (onShare) {
      onShare();
      return;
    }

    if (navigator.share) {
      try {
        await navigator.share({
          title: title,
          text: content,
        });
      } catch (error) {
        console.log('Erreur lors du partage:', error);
      }
    } else {
      // Fallback: copier dans le presse-papiers
      try {
        await navigator.clipboard.writeText(content);
        alert('Contenu copié dans le presse-papiers !');
      } catch (error) {
        console.log('Erreur lors de la copie:', error);
      }
    }
  };

  return (
    <div className={`flex flex-wrap gap-3 pt-4 border-t ${className}`}>
      {showEdit && (
        <Button onClick={onEdit} variant="outline">
          ✏️ Modifier
        </Button>
      )}
      
      {showSave && (
        <Button onClick={onSave} className="bg-green-600 hover:bg-green-700">
          💾 Sauvegarder
        </Button>
      )}
      
      <Button onClick={handleDownload} variant="outline">
        📥 Télécharger
      </Button>
      
      <Button onClick={handleShare} variant="outline">
        📤 Partager
      </Button>
    </div>
  );
};

export default ActionButtons;
