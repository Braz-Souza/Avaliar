/**
 * AddQuestionButtons Component
 * Button for adding new questions
 */

import { Plus } from 'lucide-react';

interface AddQuestionButtonsProps {
  onAddQuestion: () => void;
}

export function AddQuestionButtons({ onAddQuestion }: AddQuestionButtonsProps) {
  return (
    <div className="flex gap-3 pt-2">
      <button
        className="btn btn-primary btn-lg gap-2 flex-1 shadow-lg"
        onClick={onAddQuestion}
      >
        <Plus className="w-5 h-5" />
        Adicionar Questão
      </button>
    </div>
  );
}
