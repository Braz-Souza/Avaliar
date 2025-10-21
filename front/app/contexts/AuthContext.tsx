import React, { createContext, useContext, useState, useEffect } from 'react';
import { api, authApi } from '../services/api';

interface User {
  id: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (pin: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Verificar se há token salvo no localStorage
    const savedToken = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('auth_user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
      // Configurar o header Authorization para todas as requisições
      api.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
    }
    
    setIsLoading(false);
  }, []);

  const login = async (pin: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      // Fazer requisição para o backend com o PIN
      const loginResponse = await authApi.login(pin);
      
      const newToken = loginResponse.access_token;
      
      // Configurar o header Authorization temporariamente para buscar informações do usuário
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      
      // Buscar informações do usuário
      const userInfo = await authApi.me();
      
      const userData = {
        id: userInfo.user_id,
        name: userInfo.user_id, // Usar o user_id como nome por enquanto
      };
      
      // Salvar no estado e localStorage
      setToken(newToken);
      setUser(userData);
      localStorage.setItem('auth_token', newToken);
      localStorage.setItem('auth_user', JSON.stringify(userData));
      
      return true;
    } catch (error) {
      console.error('Erro no login:', error);
      // Remover o header se houve erro
      delete api.defaults.headers.common['Authorization'];
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    delete api.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    login,
    logout,
    isLoading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};