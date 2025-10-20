/**
 * QuestionCard Component
 * Displays and manages a single question with its options
 */

import { Trash2, Check } from 'lucide-react';
import type { Question } from '../../types/question';

interface QuestionCardProps {
  question: Question;
  index: number;
  onUpdateQuestion: (id: string, text: string) => void;
  onRemoveQuestion: (id: string) => void;
  onUpdateOption: (questionId: string, optionId: string, text: string) => void;
  onToggleCorrect: (questionId: string, optionId: string) => void;
  onRemoveOption: (questionId: string, optionId: string) => void;
  onAddOption: (questionId: string) => void;
}

export function QuestionCard({
  question,
  index,
  onUpdateQuestion,
  onRemoveQuestion,
  onUpdateOption,
  onToggleCorrect,
  onRemoveOption,
  onAddOption,
}: QuestionCardProps) {
  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        {/* Question Header */}
        <div className="flex items-start gap-3 mb-4">
          <div className="badge badge-lg badge-primary">
            {index + 1}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="badge badge-outline">
                {question.type === 'simple' ? 'Questão Simples' : 'Múltipla Escolha'}
              </span>
            </div>
            <textarea
              className="textarea textarea-bordered w-full"
              placeholder="Digite a pergunta..."
              value={question.text}
              onChange={(e) => onUpdateQuestion(question.id, e.target.value)}
              rows={2}
            />
          </div>
          <button
            className="btn btn-ghost btn-sm text-error"
            onClick={() => onRemoveQuestion(question.id)}
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>

        {/* Options */}
        <div className="space-y-2 ml-12">
          {question.options.map((option, optIndex) => (
            <div key={option.id} className="flex items-center gap-2">
              <span className="badge badge-neutral">
                {String.fromCharCode(97 + optIndex)})
              </span>
              <input
                type="text"
                className="input input-bordered flex-1"
                placeholder="Digite a opção de resposta..."
                value={option.text}
                onChange={(e) => onUpdateOption(question.id, option.id, e.target.value)}
              />
              <button
                className={`btn btn-sm ${
                  option.isCorrect 
                    ? 'btn-success' 
                    : 'btn-ghost'
                }`}
                onClick={() => onToggleCorrect(question.id, option.id)}
                title={option.isCorrect ? 'Resposta correta' : 'Marcar como correta'}
              >
                <Check className="w-4 h-4" />
              </button>
              {question.options.length > 2 && (
                <button
                  className="btn btn-ghost btn-sm text-error"
                  onClick={() => onRemoveOption(question.id, option.id)}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}
          
          {/* Add Option Button */}
          <button
            className="btn btn-ghost btn-sm gap-2 ml-8"
            onClick={() => onAddOption(question.id)}
          >
            <span className="text-lg">+</span>
            Adicionar opção
          </button>
        </div>
      </div>
    </div>
  );
}
