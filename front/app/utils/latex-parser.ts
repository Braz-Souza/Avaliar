/**
 * Utility functions for parsing and converting LaTeX content
 */

import type { Question, QuestionOption } from '../types/question';

/**
 * Parses LaTeX content into Question objects
 */
export function parseLatexToQuestions(latex: string): Question[] {
  const questions: Question[] = [];
  const lines = latex.split('\n');
  let currentQuestion: Question | null = null;
  let optionIndex = 0;

  for (const line of lines) {
    const trimmed = line.trim();

    if (trimmed.startsWith('Q:')) {
      if (currentQuestion) questions.push(currentQuestion);
      currentQuestion = {
        id: Date.now().toString() + Math.random(),
        text: trimmed.substring(2).trim(),
        options: [],
      };
      optionIndex = 0;
    } else if (trimmed.startsWith('QM:')) {
      // Convert QM: to Q: for backward compatibility
      if (currentQuestion) questions.push(currentQuestion);
      currentQuestion = {
        id: Date.now().toString() + Math.random(),
        text: trimmed.substring(3).trim(),
        options: [],
      };
      optionIndex = 0;
    } else if (trimmed.match(/^[a-z]\)/)) {
      if (currentQuestion) {
        const hasAsterisk = trimmed.endsWith('*');
        const text = trimmed.substring(2).trim().replace(/\*$/, '').trim();
        currentQuestion.options.push({
          id: Date.now().toString() + optionIndex++,
          text,
          isCorrect: hasAsterisk,
        });
      }
    }
  }

  if (currentQuestion) questions.push(currentQuestion);
  return questions;
}

/**
 * Converts Question objects to LaTeX format
 */
export function questionsToLatex(questions: Question[]): string {
  return questions.map(q => {
    const questionLine = `Q: ${q.text}`;
    const optionLines = q.options.map((opt, idx) => {
      const letter = String.fromCharCode(97 + idx);
      const asterisk = opt.isCorrect ? ' *' : '';
      return `${letter}) ${opt.text}${asterisk}`;
    }).join('\n');
    return `${questionLine}\n${optionLines}`;
  }).join('\n\n');
}
