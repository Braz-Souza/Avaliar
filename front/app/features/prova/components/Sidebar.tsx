/**
 * Sidebar Component
 * Navigation and actions sidebar for prova editor
 */

import { ArrowLeft, Download, FileText, Eye, Save } from 'lucide-react';
import { NavLink } from 'react-router';
import type { PreviewMode } from '../../../types/question';

interface SidebarProps {
  provaName?: string;
  currentProvaId?: string | null;
  isCompiling: boolean;
  previewMode: PreviewMode;
  onPreviewModeChange: (mode: PreviewMode) => void;
  onSave: () => void;
  onDownloadPDF: () => void;
  onDownloadLatex: () => void;
}

export function Sidebar({
  provaName,
  currentProvaId,
  isCompiling,
  previewMode,
  onPreviewModeChange,
  onSave,
  onDownloadPDF,
  onDownloadLatex,
}: SidebarProps) {
  return (
    <aside className="w-72 bg-base-100 shadow-2xl flex flex-col border-r border-base-300">
      {/* Logo/Header */}
      <div className="p-6 border-b border-base-300">
        <NavLink to="/" className="flex items-center gap-3 group">
          <div className="btn btn-circle btn-primary btn-sm">
            <ArrowLeft className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-primary">Avaliar</h1>
            <p className="text-xs text-base-content/60">Editor de Provas</p>
          </div>
        </NavLink>
      </div>

      {/* Status Section */}
      <div className="p-6 border-b border-base-300 space-y-3">
        {provaName && (
          <div>
            <label className="text-xs font-semibold text-base-content/60 uppercase tracking-wide">
              Prova Atual
            </label>
            <p className="text-sm font-medium mt-1 truncate">{provaName}</p>
          </div>
        )}
        <div className="flex flex-wrap gap-2">
          <div className="badge badge-primary gap-1">
            <FileText className="w-3 h-3" />
            Editor
          </div>
          {currentProvaId && (
            <div className="badge badge-success gap-1">
              <Save className="w-3 h-3" />
              Salvo
            </div>
          )}
          {isCompiling && (
            <div className="badge badge-warning gap-1">
              <span className="loading loading-spinner loading-xs"></span>
              Compilando
            </div>
          )}
        </div>
      </div>

      {/* Main Actions */}
      <div className="flex-1 p-6 space-y-4 overflow-y-auto">
        {/* Save Section */}
        <div>
          <label className="text-xs font-semibold text-base-content/60 uppercase tracking-wide mb-3 block">
            Ações Principais
          </label>
          <button
            className="btn btn-success w-full gap-2 justify-start"
            onClick={onSave}
          >
            <Save className="w-5 h-5" />
            <span className="flex-1 text-left">
              {currentProvaId ? 'Atualizar Prova' : 'Salvar Prova'}
            </span>
          </button>
        </div>

        {/* Preview Mode */}
        <div>
          <label className="text-xs font-semibold text-base-content/60 uppercase tracking-wide mb-3 block">
            Visualização
          </label>
          <div className="space-y-2">
            <button
              className={`btn w-full gap-2 justify-start ${
                previewMode === 'pdf' ? 'btn-primary' : 'btn-ghost'
              }`}
              onClick={() => onPreviewModeChange('pdf')}
            >
              <Eye className="w-5 h-5" />
              <span className="flex-1 text-left">Pré-visualizar PDF</span>
            </button>
            <button
              className={`btn w-full gap-2 justify-start ${
                previewMode === 'latex' ? 'btn-primary' : 'btn-ghost'
              }`}
              onClick={() => onPreviewModeChange('latex')}
            >
              <FileText className="w-5 h-5" />
              <span className="flex-1 text-left">Código LaTeX</span>
            </button>
          </div>
        </div>

        {/* Download Section */}
        <div>
          <label className="text-xs font-semibold text-base-content/60 uppercase tracking-wide mb-3 block">
            Downloads
          </label>
          <div className="space-y-2">
            <button
              className="btn btn-outline btn-primary w-full gap-2 justify-start"
              onClick={onDownloadPDF}
              disabled={isCompiling}
            >
              <Download className="w-5 h-5" />
              <span className="flex-1 text-left">
                {isCompiling ? 'Compilando...' : 'Baixar PDF'}
              </span>
            </button>
            <button
              className="btn btn-outline btn-secondary w-full gap-2 justify-start"
              onClick={onDownloadLatex}
            >
              <FileText className="w-5 h-5" />
              <span className="flex-1 text-left">Baixar LaTeX</span>
            </button>
          </div>
        </div>

        {/* Help Section */}
        <div className="pt-4">
          <div className="alert alert-info shadow-lg">
            <div>
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <div className="text-xs">
                <p className="font-semibold mb-1">Formato de Questões:</p>
                <p className="opacity-80">Q: questão simples</p>
                <p className="opacity-80">QM: múltipla escolha</p>
                <p className="opacity-80">a), b), c)... opções</p>
                <p className="opacity-80">* marca resposta correta</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-6 border-t border-base-300">
        <div className="text-xs text-base-content/50 text-center">
          <p>Avaliar v0.0</p>
          <p className="mt-1">Sistema de Provas</p>
        </div>
      </div>
    </aside>
  );
}
