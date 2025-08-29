import React from 'react';

const CareerForm = ({ onSubmit }) => {
  return (
    <form onSubmit={onSubmit}>
      <input name="objectif" placeholder="Objectif de carrière" />
      <button type="submit">Envoyer</button>
    </form>
  );
};

export default CareerForm; 