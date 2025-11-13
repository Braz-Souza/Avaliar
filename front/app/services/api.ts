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

// Turma Types
export interface TurmaData {
  ano: number;
  materia: string;
  curso: string;
  periodo: number;
}

export interface TurmaInfo {
  id: string;
  ano: number;
  materia: string;
  curso: string;
  periodo: number;
}

// Aluno Types
export interface AlunoData {
  nome: string;
  email?: string;
  matricula: string;
  turma_ids: string[];
}

export interface AlunoInfo {
  id: string;
  nome: string;
  email?: string;
  matricula: string;
  turmas: TurmaInfo[];
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

// Turmas API
export const turmasApi = {
  // List all turmas
  list: async (params?: {
    skip?: number;
    limit?: number;
    ano?: number;
    materia?: string;
    curso?: string;
  }): Promise<TurmaInfo[]> => {
    const response = await api.get('/turmas', { params });
    return response.data;
  },

  // Get a specific turma by ID
  get: async (turmaId: string): Promise<TurmaInfo> => {
    const response = await api.get(`/turmas/${turmaId}`);
    return response.data;
  },

  // Create a new turma
  create: async (turma: TurmaData): Promise<TurmaInfo> => {
    const response = await api.post('/turmas', turma);
    return response.data;
  },

  // Update an existing turma
  update: async (turmaId: string, turma: Partial<TurmaData>): Promise<TurmaInfo> => {
    const response = await api.put(`/turmas/${turmaId}`, turma);
    return response.data;
  },

  // Delete a turma
  delete: async (turmaId: string): Promise<void> => {
    await api.delete(`/turmas/${turmaId}`);
  },

  // Count turmas
  count: async (params?: {
    ano?: number;
    materia?: string;
    curso?: string;
  }): Promise<{ total: number }> => {
    const response = await api.get('/turmas/count/total', { params });
    return response.data;
  },
};

// Alunos API
export const alunosApi = {
  // List all alunos
  list: async (params?: {
    skip?: number;
    limit?: number;
    nome?: string;
    email?: string;
    matricula?: string;
    turma_id?: string;
  }): Promise<AlunoInfo[]> => {
    const response = await api.get('/alunos', { params });
    return response.data;
  },

  // Get a specific aluno by ID
  get: async (alunoId: string): Promise<AlunoInfo> => {
    const response = await api.get(`/alunos/${alunoId}`);
    return response.data;
  },

  // Create a new aluno
  create: async (aluno: AlunoData): Promise<AlunoInfo> => {
    const response = await api.post('/alunos', aluno);
    return response.data;
  },

  // Update an existing aluno
  update: async (alunoId: string, aluno: Partial<AlunoData>): Promise<AlunoInfo> => {
    const response = await api.put(`/alunos/${alunoId}`, aluno);
    return response.data;
  },

  // Delete an aluno
  delete: async (alunoId: string): Promise<void> => {
    await api.delete(`/alunos/${alunoId}`);
  },

  // Add aluno to turma
  addToTurma: async (alunoId: string, turmaId: string): Promise<AlunoInfo> => {
    const response = await api.post(`/alunos/${alunoId}/turmas/${turmaId}`);
    return response.data;
  },

  // Remove aluno from turma
  removeFromTurma: async (alunoId: string, turmaId: string): Promise<AlunoInfo> => {
    const response = await api.delete(`/alunos/${alunoId}/turmas/${turmaId}`);
    return response.data;
  },

  // Count alunos
  count: async (params?: {
    nome?: string;
    email?: string;
    matricula?: string;
    turma_id?: string;
  }): Promise<{ total: number }> => {
    const response = await api.get('/alunos/count/total', { params });
    return response.data;
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

// Exam Correction API
export interface QuestionDetail {
  question: number;
  detected: string | null;
  correct_answer: string;
  status: 'correct' | 'wrong' | 'blank';
}

export interface ExamCorrectionResult {
  total: number;
  correct: number;
  wrong: number;
  blank: number;
  score: number;
  score_percentage: number;
  details: QuestionDetail[];
}

export const examCorrectorApi = {
  // Correct a single exam from an image
  correct: async (
    imageFile: File,
    answerKey: string[],
    numQuestions: number,
    numOptions: number = 5
  ): Promise<ExamCorrectionResult> => {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('answer_key', JSON.stringify(answerKey));
    formData.append('num_questions', numQuestions.toString());
    formData.append('num_options', numOptions.toString());

    const response = await api.post('/exam-corrector/correct', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Validate answer key
  validateAnswerKey: async (
    answerKey: string[],
    numOptions: number = 5
  ): Promise<{ valid: boolean; message: string }> => {
    const formData = new FormData();
    formData.append('answer_key', JSON.stringify(answerKey));
    formData.append('num_options', numOptions.toString());

    const response = await api.post('/exam-corrector/validate-answer-key', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
