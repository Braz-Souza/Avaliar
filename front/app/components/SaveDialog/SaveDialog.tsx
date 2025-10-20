/**
 * SaveDialog Component
 * Modal dialog for saving prova
 */

import { Save } from 'lucide-react';
import type { RefObject } from 'react';

interface SaveDialogProps {
  dialogRef: RefObject<HTMLDialogElement | null>;
  provaName: string;
  onNameChange: (name: string) => void;
  onSave: () => void;
  onClose: () => void;
  isSaving: boolean;
  saveError: string | null;
  isUpdate: boolean;
}

export function SaveDialog({
  dialogRef,
  provaName,
  onNameChange,
  onSave,
  onClose,
  isSaving,
  saveError,
  isUpdate,
}: SaveDialogProps) {
  return (
    <dialog ref={dialogRef} className="modal modal-bottom sm:modal-middle">
      <div className="modal-box">
        <h3 className="font-bold text-lg flex items-center gap-2 mb-4">
          <Save className="w-5 h-5" />
          {isUpdate ? 'Atualizar Prova' : 'Nova Prova'}
        </h3>
        
        <div className="form-control w-full">
          <label className="label">
            <span className="label-text font-medium">Nome da Prova</span>
            <span className="label-text-alt text-base-content/50">Obrigatório</span>
          </label>
          <input
            type="text"
            placeholder="Ex: Prova de Matemática - Unidade 1"
            className="input input-bordered w-full"
            value={provaName}
            onChange={(e) => onNameChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                onSave();
              }
            }}
            autoFocus
          />
          <label className="label">
            <span className="label-text-alt text-base-content/50">
              Pressione Enter para salvar rapidamente
            </span>
          </label>
        </div>

        {saveError && (
          <div className="alert alert-error mt-4">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="text-sm">{saveError}</span>
          </div>
        )}

        <div className="modal-action">
          <button
            className="btn btn-ghost"
            onClick={onClose}
            disabled={isSaving}
          >
            Cancelar
          </button>
          <button
            className={`btn btn-success gap-2 ${isSaving ? 'btn-disabled' : ''}`}
            onClick={onSave}
            disabled={isSaving}
          >
            {isSaving && <span className="loading loading-spinner loading-sm"></span>}
            {isSaving ? 'Salvando...' : (isUpdate ? 'Atualizar' : 'Salvar')}
          </button>
        </div>
      </div>
      <form method="dialog" className="modal-backdrop">
        <button onClick={onClose}>close</button>
      </form>
    </dialog>
  );
}
