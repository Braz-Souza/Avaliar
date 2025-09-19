import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE,
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