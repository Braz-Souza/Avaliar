import axios from 'axios';
import { API_CONFIG } from '../config/api';

export const api = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para debug
api.interceptors.request.use(
  (config) => {
    console.log('🔵 Request:', {
      method: config.method,
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      headers: config.headers,
    });
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log('✅ Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data,
    });
    return response;
  },
  (error) => {
    console.error('❌ Response Error:', {
      status: error.response?.status,
      url: error.config?.url,
      data: error.response?.data,
    });
    return Promise.reject(error);
  }
);

// Types
export interface ProvaData {
  name: string;
  content: string;
}

export interface ProvaInfo {
  id: string;
  name: string;
  created_at: string;
  modified_at: string;
}

// Provas API
export const provasApi = {
  // List all saved provas
  list: async (): Promise<ProvaInfo[]> => {
    const response = await api.get('/provas');
    return response.data;
  },

  // Get a specific prova by ID
  get: async (provaId: string): Promise<ProvaData> => {
    const response = await api.get(`/provas/${provaId}`);
    return response.data;
  },

  // Save a new prova
  create: async (prova: ProvaData): Promise<ProvaInfo> => {
    const response = await api.post('/provas', prova);
    return response.data;
  },

  // Update an existing prova
  update: async (provaId: string, prova: ProvaData): Promise<ProvaInfo> => {
    const response = await api.put(`/provas/${provaId}`, prova);
    return response.data;
  },

  // Delete a prova
  delete: async (provaId: string): Promise<void> => {
    await api.delete(`/provas/${provaId}`);
  },
};

// Auth API
export interface LoginRequest {
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserInfoResponse {
  user_id: string;
  authenticated: boolean;
}

export const authApi = {
  // Login with PIN
  login: async (pin: string): Promise<LoginResponse> => {
    const response = await api.post('/auth/login', { password: pin });
    return response.data;
  },
  
  // Get current user info
  me: async (): Promise<UserInfoResponse> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};