/**
 * PreviewPanel Component
 * PDF and LaTeX preview panel
 */

import { Eye, ExternalLink } from 'lucide-react';
import type { PreviewMode } from '../../../types/question';
import LaTeXCompiler from '../../../services/tex';
import { AnswerSheetPreview } from './AnswerSheetPreview';

interface PreviewPanelProps {
  previewMode: PreviewMode;
  pdfUrl: string | null;
  pdfLoadError: boolean;
  isCompiling: boolean;
  latexContent: string;
  onPdfLoadError: () => void;
  answerSheetUrl: string | null;
  answerSheetLoadError: boolean;
  onAnswerSheetLoadError: () => void;
}

export function PreviewPanel({
  previewMode,
  pdfUrl,
  pdfLoadError,
  isCompiling,
  latexContent,
  onPdfLoadError,
  answerSheetUrl,
  answerSheetLoadError,
  onAnswerSheetLoadError,
}: PreviewPanelProps) {
  const getLatexPreview = () => {
    return LaTeXCompiler.generateAMCDocument(latexContent);
  };

  // Show answer sheet preview
  if (previewMode === 'answer-sheet') {
    return (
      <AnswerSheetPreview
        answerSheetUrl={answerSheetUrl}
        pdfLoadError={answerSheetLoadError}
        isCompiling={isCompiling}
        onPdfLoadError={onAnswerSheetLoadError}
      />
    );
  }

  return (
    <div className="flex-1 flex flex-col p-6 pl-0 overflow-hidden">
      <div className="card bg-base-100 shadow-xl flex-1 flex flex-col overflow-hidden border border-base-300">
        <div className="card-body p-0 flex-1 flex flex-col overflow-hidden">
          {/* Preview Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-base-300 bg-gradient-to-r from-secondary/10 to-accent/10">
            <div className="flex items-center gap-2">
              <div className="avatar placeholder">
                <div className="bg-secondary text-secondary-content rounded-full w-8 flex items-center justify-center">
                  <Eye className="w-4 h-4 m-2" />
                </div>
              </div>
              <h2 className="text-lg font-semibold">
                {previewMode === 'pdf' ? 'Pré-visualização PDF' : 'Código LaTeX'}
              </h2>
            </div>
            {pdfUrl && previewMode === 'pdf' && (
              <a
                href={pdfUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-sm btn-ghost gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                Nova aba
              </a>
            )}
          </div>

          {/* Preview Content */}
          <div className="flex-1 overflow-hidden bg-base-200">
            {previewMode === 'pdf' ? (
              pdfUrl ? (
                pdfLoadError ? (
                  <div className="flex items-center justify-center h-full p-8">
                    <div className="card bg-base-100 shadow-xl max-w-md">
                      <div className="card-body text-center space-y-4">
                        <ExternalLink className="w-16 h-16 mx-auto text-error" />
                        <div>
                          <h3 className="text-lg font-bold mb-2">Erro ao carregar PDF</h3>
                          <p className="text-sm text-base-content/70">
                            O navegador não conseguiu exibir o PDF
                          </p>
                        </div>
                        <a
                          href={pdfUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn btn-primary gap-2"
                        >
                          <ExternalLink className="w-4 h-4" />
                          Abrir em nova aba
                        </a>
                      </div>
                    </div>
                  </div>
                ) : (
                  <iframe
                    src={pdfUrl}
                    className="w-full h-full border-0"
                    title="PDF Preview"
                    onLoad={() => {
                      console.log('PDF carregado com sucesso no iframe');
                      console.log('URL do iframe:', pdfUrl);
                    }}
                    onError={(e) => {
                      console.error('Erro ao carregar iframe:', e);
                      console.error('URL que falhou:', pdfUrl);
                      onPdfLoadError();
                    }}
                  />
                )
              ) : (
                <div className="flex items-center justify-center h-full p-8">
                  <div className="card bg-base-100 shadow-xl max-w-md">
                    <div className="card-body text-center space-y-4">
                      <Eye className="w-16 h-16 mx-auto text-base-content/30" />
                      <div>
                        <h3 className="text-lg font-bold mb-2">Aguardando conteúdo</h3>
                        <p className="text-sm text-base-content/70">
                          {isCompiling ? 'Compilando documento...' : 'Digite no editor para gerar o PDF'}
                        </p>
                      </div>
                      {isCompiling && (
                        <progress className="progress progress-primary w-56"></progress>
                      )}
                    </div>
                  </div>
                </div>
              )
            ) : (
              <div className="h-full overflow-auto">
                <div className="mockup-code h-full">
                  <pre className="px-6"><code className="text-sm">{getLatexPreview()}</code></pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
