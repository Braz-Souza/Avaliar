/**
 * Configurações da API baseadas no ambiente
 */

interface ApiConfig {
  baseURL: string;
  timeout: number;
}

/**
 * Detecta o ambiente e retorna a configuração apropriada
 */
function getApiConfig(): ApiConfig {
  // Verifica se estamos em produção
  const isProduction = process.env.NODE_ENV === 'production';
  
  // Verifica se estamos rodando no Docker
  const isDocker = typeof window !== 'undefined' && window.location.hostname !== 'localhost';
  
  let baseURL: string;
  
  // Permite sobrescrita via variável de ambiente
  if (process.env.VITE_API_BASE_URL) {
    baseURL = process.env.VITE_API_BASE_URL;
  } else if (isProduction || isDocker) {
    // Em produção ou Docker, usa URL relativa (mesmo servidor)
    baseURL = '/api';
  } else {
    // Em desenvolvimento local, usa porta padrão do backend
    baseURL = 'http://localhost:8000/api';
  }
  
  return {
    baseURL,
    timeout: 30000, // 30 segundos
  };
}

export const API_CONFIG = getApiConfig();

/**
 * Gera URL completa para recursos (PDFs, etc.)
 */
export function getResourceUrl(path: string): string {
  const isProduction = process.env.NODE_ENV === 'production';
  const isDocker = typeof window !== 'undefined' && window.location.hostname !== 'localhost';
  
  // Permite sobrescrita via variável de ambiente
  if (process.env.VITE_API_BASE_URL) {
    const baseUrl = process.env.VITE_API_BASE_URL.replace('/api', '');
    return `${baseUrl}${path}`;
  } else if (isProduction || isDocker) {
    // Em produção ou Docker, usa URL relativa
    return path;
  } else {
    // Em desenvolvimento, usa URL completa
    return `http://localhost:8000${path}`;
  }
}