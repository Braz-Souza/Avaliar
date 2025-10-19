import axios from 'axios';
import { API_CONFIG } from '../config/api';

export const api = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const healthApi = {
  get: async (): Promise<{ status: string; }> => {
    const response = await api.get('/health');
    return response.data;
  },
}