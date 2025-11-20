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

// Randomization Types
export interface TurmaProvaInfo {
  id: string;
  turma_id: string;
  prova_id: string;
  created_at: string;
}

export interface AlunoRandomizacaoInfo {
  id: string;
  turma_prova_id: string;
  aluno_id: string;
  questoes_order: number[];
  alternativas_order: { [key: string]: number[] };
  created_at: string;
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

// Randomization API
export const randomizacaoApi = {
  // Link prova to turma
  linkProvaToTurma: async (turmaId: string, provaId: string): Promise<TurmaProvaInfo> => {
    const response = await api.post(`/randomizacao/link/${turmaId}/${provaId}`);
    return response.data;
  },

  // List turma-prova links
  listTurmasProvas: async (params?: {
    turma_id?: string;
    prova_id?: string;
  }): Promise<TurmaProvaInfo[]> => {
    const response = await api.get('/randomizacao/turmas-provas', { params });
    return response.data;
  },

  // Get aluno randomizacoes for turma-prova
  getAlunosRandomizacoes: async (turmaProvaId: string): Promise<AlunoRandomizacaoInfo[]> => {
    const response = await api.get(`/randomizacao/alunos/${turmaProvaId}`);
    return response.data;
  },

  // Get specific aluno randomizacao
  getAlunoRandomizacao: async (alunoId: string, provaId: string): Promise<AlunoRandomizacaoInfo> => {
    const response = await api.get(`/randomizacao/aluno/${alunoId}/prova/${provaId}`);
    return response.data;
  },

  // Unlink prova from turma
  unlinkProvaFromTurma: async (turmaId: string, provaId: string): Promise<{ message: string }> => {
    const response = await api.delete(`/randomizacao/unlink/${turmaId}/${provaId}`);
    return response.data;
  },

  // Get turmas disponiveis para prova
  getTurmasDisponiveisParaProva: async (provaId: string): Promise<{
    disponiveis: TurmaInfo[];
    vinculadas: TurmaInfo[];
  }> => {
    const response = await api.get(`/randomizacao/turmas/disponiveis/${provaId}`);
    return response.data;
  },

  // Get provas disponiveis para turma
  getProvasDisponiveisParaTurma: async (turmaId: string): Promise<{
    disponiveis: ProvaInfo[];
    vinculadas: ProvaInfo[];
  }> => {
    const response = await api.get(`/randomizacao/provas/disponiveis/${turmaId}`);
    return response.data;
  },

  // Generate PDF for aluno
  generateAlunoProvaPdf: async (alunoId: string, provaId: string): Promise<{
    pdfUrl: string;
    message: string;
  }> => {
    const response = await api.get(`/randomizacao/pdf/${alunoId}/${provaId}`);
    return response.data;
  },

  // Download personalized PDF for aluno (returns blob)
  downloadAlunoProvaPdf: async (alunoId: string, provaId: string): Promise<Blob> => {
    const response = await api.get(`/randomizacao/aluno/${alunoId}/prova/${provaId}/content`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Download ZIP with all PDFs for a turma-prova
  downloadAllProvasZip: async (turmaProvaId: string): Promise<Blob> => {
    const response = await api.get(`/randomizacao/download-zip/${turmaProvaId}`, {
      responseType: 'blob'
    });
    return response.data;
  },

  // Download gabarito personalizado do aluno PDF
  downloadGabaritoAluno: async (alunoId: string, provaId: string): Promise<Blob> => {
    const response = await api.get(`/randomizacao/gabarito/${alunoId}/${provaId}`, {
      responseType: 'blob'
    });
    return response.data;
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

  // Delete a aluno
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

// Image Correction API
export interface ImageCorrectionResponse {
  id: string;
  aluno_id: string;
  turma_id: string;
  prova_id: string;
  corrigido_por: string;
  data_correcao: string;
  nota: number | null;
  total_questoes: number;
  acertos: number | null;
  respostas: Array<{
    id: string;
    correcao_id: string;
    questao_numero: number;
    resposta_marcada: string;
    resposta_correta: string | null;
    esta_correta: boolean | null;
  }>;
  aluno?: any;
  turma?: any;
  prova?: any;
  corretor?: any;
}

export const imageCorrectionApi = {
  // Upload image and process
  uploadAndProcess: async (
    imageFile: File,
    alunoId: string,
    turmaId: string,
    provaId: string
  ): Promise<ImageCorrectionResponse> => {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('aluno_id', alunoId);
    formData.append('turma_id', turmaId);
    formData.append('prova_id', provaId);

    const response = await api.post('/image-correction/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
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
