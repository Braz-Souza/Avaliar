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
  const isProduction = import.meta.env.PROD;
  
  const envBaseUrl = import.meta.env.VITE_API_BASE_URL;
  
  let baseURL: string;
  
  if (envBaseUrl) {
    baseURL = envBaseUrl;
  } else {
    baseURL = 'http://localhost:8000/api';
  }
  
  return {
    baseURL,
    timeout: 30000,
  };
}

export const API_CONFIG = getApiConfig();

/**
 * Gera URL completa para recursos (PDFs, etc.)
 */
export function getResourceUrl(path: string): string {
  const fullPath = path.startsWith('/api/') ? path : `/api${path}`;
  
  if (typeof window !== 'undefined') {
    const envBaseUrl = import.meta.env.VITE_API_BASE_URL;

    const baseUrl = envBaseUrl 
      ? envBaseUrl.replace('/api', '')
      : 'http://localhost:8000';
    
    return `${baseUrl}${fullPath}`;
  }
  
  return fullPath;
}