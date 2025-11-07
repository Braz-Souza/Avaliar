/**
 * Types for questions and options
 */

export interface QuestionOption {
  id: string;
  text: string;
  isCorrect: boolean;
}

export interface Question {
  id: string;
  type: 'simple' | 'multiple';
  text: string;
  options: QuestionOption[];
}

export type EditMode = 'visual' | 'code';
export type PreviewMode = 'pdf' | 'latex' | 'answer-sheet' | 'answer-key';
