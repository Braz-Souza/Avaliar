/**
 * AddQuestionButtons Component
 * Buttons for adding new questions
 */

import { Plus } from 'lucide-react';

interface AddQuestionButtonsProps {
  onAddSimple: () => void;
  onAddMultiple: () => void;
}

export function AddQuestionButtons({ onAddSimple, onAddMultiple }: AddQuestionButtonsProps) {
  return (
    <div className="flex gap-3 pt-2">
      <button
        className="btn btn-primary btn-lg gap-2 flex-1 shadow-lg"
        onClick={onAddSimple}
      >
        <Plus className="w-5 h-5" />
        Adicionar Questão Simples
      </button>
      <button
        className="btn btn-secondary btn-lg gap-2 flex-1 shadow-lg"
        onClick={onAddMultiple}
      >
        <Plus className="w-5 h-5" />
        Adicionar Múltipla Escolha
      </button>
    </div>
  );
}
