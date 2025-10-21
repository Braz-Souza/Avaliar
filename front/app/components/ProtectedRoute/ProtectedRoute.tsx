import React from 'react';
import { Navigate } from 'react-router';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, isLoading } = useAuth();

  // Mostrar loading enquanto verifica a autenticação
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  // Se não estiver logado, redirecionar para login
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Se estiver logado, renderizar o conteúdo protegido
  return <>{children}</>;
};

export default ProtectedRoute;