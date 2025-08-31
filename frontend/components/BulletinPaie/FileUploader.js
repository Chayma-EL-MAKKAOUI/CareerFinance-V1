import React, { useRef } from 'react';

const FileUploader = ({ onFileSelect }) => {
  const fileInputRef = useRef(null);

  const handleClick = () => {
    fileInputRef.current.click(); // clique simulé sur input invisible
  };

  const handleChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <div
      onClick={handleClick}
      style={{
        cursor: 'pointer',
        border: '2px dashed #3b82f6',
        borderRadius: '12px',
        padding: '40px',
        textAlign: 'center',
        background: '#f9f9ff'
      }}
    >
      <input
        type="file"
        accept=".pdf,.png,.jpg"
        ref={fileInputRef}
        onChange={handleChange}
        style={{ display: 'none' }} // invisible mais déclenché au clic
      />
      <div>
        <span style={{ fontSize: '32px' }}>📤</span>
        <p style={{ color: '#2563eb', fontWeight: 'bold' }}>
          Déposez votre bulletin de paie ou contrat ici
        </p>
        <p style={{ fontSize: '14px', color: 'gray' }}>
          Format acceptés : PDF, JPG, PNG • Taille max : 10MB
        </p>
      </div>
    </div>
  );
};

export default FileUploader;
