import React, { useState } from 'react';
import { Navigate, useNavigate } from 'react-router';
import { useAuth } from '../../contexts/AuthContext';

const LoginPage: React.FC = () => {
  const [pin, setPin] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login, user } = useAuth();
  const navigate = useNavigate();

  // Se já estiver logado, redirecionar para a página principal
  if (user) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!pin.trim()) {
      setError('Por favor, digite o PIN');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const success = await login(pin);
      
      if (success) {
        navigate('/', { replace: true });
      } else {
        setError('PIN inválido. Tente novamente.');
      }
    } catch (err) {
      setError('Erro ao fazer login. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Permitir apenas números e limitar a 6 dígitos
    if (/^\d{0,6}$/.test(value)) {
      setPin(value);
      setError('');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Avaliar - Login
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Digite seu PIN para acessar o sistema
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="pin" className="block text-sm font-medium text-gray-700 mb-2">
              PIN (6 dígitos)
            </label>
            <input
              id="pin"
              name="pin"
              type="password"
              value={pin}
              onChange={handlePinChange}
              className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm text-center text-2xl tracking-widest"
              placeholder="••••••"
              maxLength={6}
              autoFocus
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center bg-red-50 border border-red-200 rounded-md p-2">
              {error}
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading || pin.length !== 6}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Entrando...
                </div>
              ) : (
                'Entrar'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;