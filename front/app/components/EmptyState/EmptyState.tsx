/**
 * EmptyState Component
 * Displays when there are no questions
 */

import { FileText } from 'lucide-react';

export function EmptyState() {
  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body text-center py-12">
        <FileText className="w-16 h-16 mx-auto text-base-content/30 mb-4" />
        <h3 className="text-lg font-bold mb-2">Nenhuma questão adicionada</h3>
        <p className="text-sm text-base-content/70">
          Clique nos botões abaixo para adicionar sua primeira questão
        </p>
      </div>
    </div>
  );
}
