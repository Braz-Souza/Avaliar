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
  } else {
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
 * SEMPRE retorna URL absoluta para evitar que o React Router intercepte
 */
export function getResourceUrl(path: string): string {
  // Adiciona /api/ ao path se não começar com ele
  const fullPath = path.startsWith('/api/') ? path : `/api${path}`;
  
  // Para recursos (PDFs), sempre usar URL absoluta
  // Isso evita que o React Router tente interpretar como rota
  if (typeof window !== 'undefined') {
    const baseUrl = process.env.VITE_API_BASE_URL 
      ? process.env.VITE_API_BASE_URL.replace('/api', '')
      : 'http://localhost:8000';
    
    return `${baseUrl}${fullPath}`;
  }
  
  // Fallback para SSR (não deveria acontecer com PDFs)
  return fullPath;
}