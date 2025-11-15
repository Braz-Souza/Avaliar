/**
 * Custom hook for managing prova editor state and logic
 */

import { useState, useEffect } from 'react';
import type { Question, EditMode } from '../types/question';
import { parseLatexToQuestions, questionsToLatex } from '../utils/latex-parser';

const INITIAL_LATEX = `Q: Qual é a capital do Brasil?
a) São Paulo
b) Brasília *
c) Rio de Janeiro
d) Belo Horizonte

QM: Quais das seguintes são linguagens de programação?
a) JavaScript *
b) HTML
c) Python *
d) CSS`;

export function useProvaEditor(initialContent?: string) {
  const [latexContent, setLatexContent] = useState(initialContent || INITIAL_LATEX);
  const [questions, setQuestions] = useState<Question[]>(() =>
    parseLatexToQuestions(initialContent || INITIAL_LATEX)
  );
  const [editMode, setEditMode] = useState<EditMode>('visual');

  // Sync questions with latex content when in visual mode
  useEffect(() => {
    if (editMode === 'visual') {
      const newLatex = questionsToLatex(questions);
      setLatexContent(newLatex);
    }
  }, [questions, editMode]);

  // Update questions when switching from code to visual mode
  useEffect(() => {
    if (editMode === 'visual') {
      const parsed = parseLatexToQuestions(latexContent);
      if (JSON.stringify(parsed) !== JSON.stringify(questions)) {
        setQuestions(parsed);
      }
    }
  }, [editMode]);

  const addQuestion = () => {
    const newQuestion: Question = {
      id: Date.now().toString() + Math.random(),
      text: '',
      options: [
        { id: Date.now().toString() + '0', text: '', isCorrect: false },
        { id: Date.now().toString() + '1', text: '', isCorrect: false },
      ],
    };
    setQuestions([...questions, newQuestion]);
  };

  const removeQuestion = (id: string) => {
    setQuestions(questions.filter(q => q.id !== id));
  };

  const updateQuestion = (id: string, text: string) => {
    setQuestions(questions.map(q => q.id === id ? { ...q, text } : q));
  };

  const addOption = (questionId: string) => {
    setQuestions(questions.map(q => {
      if (q.id === questionId) {
        return {
          ...q,
          options: [...q.options, {
            id: Date.now().toString() + Math.random(),
            text: '',
            isCorrect: false,
          }],
        };
      }
      return q;
    }));
  };

  const removeOption = (questionId: string, optionId: string) => {
    setQuestions(questions.map(q => {
      if (q.id === questionId) {
        return {
          ...q,
          options: q.options.filter(opt => opt.id !== optionId),
        };
      }
      return q;
    }));
  };

  const updateOption = (questionId: string, optionId: string, text: string) => {
    setQuestions(questions.map(q => {
      if (q.id === questionId) {
        return {
          ...q,
          options: q.options.map(opt =>
            opt.id === optionId ? { ...opt, text } : opt
          ),
        };
      }
      return q;
    }));
  };

  const toggleOptionCorrect = (questionId: string, optionId: string) => {
    setQuestions(questions.map(q => {
      if (q.id === questionId) {
        // For simple questions, only one option can be correct
        return {
          ...q,
          options: q.options.map(opt => ({
            ...opt,
            isCorrect: opt.id === optionId,
          })),
        };
      }
      return q;
    }));
  };

  const setContent = (content: string) => {
    setLatexContent(content);
    setQuestions(parseLatexToQuestions(content));
  };

  return {
    latexContent,
    setLatexContent,
    questions,
    editMode,
    setEditMode,
    addQuestion,
    removeQuestion,
    updateQuestion,
    addOption,
    removeOption,
    updateOption,
    toggleOptionCorrect,
    setContent,
  };
}
