'use client';
import React from 'react';
import { useAuth } from '../../lib/useAuth';
import { useRouter } from 'next/navigation';

const ProtectedModal = ({ 
  children, 
  isOpen, 
  onClose,
  redirectTo = '/auth/login'
}) => {
  const { isLoggedIn, loading } = useAuth();
  const router = useRouter();

  // Si pas connecté et modal ouvert, rediriger vers la connexion
  React.useEffect(() => {
    if (isOpen && !loading && !isLoggedIn) {
      onClose(); // Fermer la modal
      router.push(redirectTo);
    }
  }, [isOpen, isLoggedIn, loading, onClose, router, redirectTo]);

  // Si en cours de chargement, ne rien afficher
  if (loading) {
    return null;
  }

  // Si pas connecté, ne pas afficher la modal
  if (!isLoggedIn) {
    return null;
  }

  // Si connecté, afficher la modal
  return children;
};

export default ProtectedModal;
