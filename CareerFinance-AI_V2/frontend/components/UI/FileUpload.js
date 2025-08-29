import React from 'react';

const FileUpload = ({ onChange }) => {
  return <input type="file" onChange={onChange} />;
};

export default FileUpload; 