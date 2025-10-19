import axios from 'axios';
import { API_CONFIG } from '../config/api';

export const api = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

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