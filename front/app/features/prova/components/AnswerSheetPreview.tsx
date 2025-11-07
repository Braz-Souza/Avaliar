/**
 * AnswerSheetPreview Component
 * Preview of answer sheet for students to mark their answers
 */

import { ClipboardList, ExternalLink } from 'lucide-react';

interface AnswerSheetPreviewProps {
  answerSheetUrl: string | null;
  pdfLoadError: boolean;
  isCompiling: boolean;
  onPdfLoadError: () => void;
}

export function AnswerSheetPreview({
  answerSheetUrl,
  pdfLoadError,
  isCompiling,
  onPdfLoadError,
}: AnswerSheetPreviewProps) {
  return (
    <div className="flex-1 flex flex-col p-6 pl-0 overflow-hidden">
      <div className="card bg-base-100 shadow-xl flex-1 flex flex-col overflow-hidden border border-base-300">
        <div className="card-body p-0 flex-1 flex flex-col overflow-hidden">
          {/* Preview Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-base-300 bg-gradient-to-r from-info/10 to-success/10">
            <div className="flex items-center gap-2">
              <div className="avatar placeholder">
                <div className="bg-info text-info-content rounded-full w-8 flex items-center justify-center">
                  <ClipboardList className="w-4 h-4 m-2" />
                </div>
              </div>
              <h2 className="text-lg font-semibold">Cartão Resposta</h2>
            </div>
            {answerSheetUrl && (
              <a
                href={answerSheetUrl}
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
            {answerSheetUrl ? (
              pdfLoadError ? (
                <div className="flex items-center justify-center h-full p-8">
                  <div className="card bg-base-100 shadow-xl max-w-md">
                    <div className="card-body text-center space-y-4">
                      <ExternalLink className="w-16 h-16 mx-auto text-error" />
                      <div>
                        <h3 className="text-lg font-bold mb-2">Erro ao carregar Cartão Resposta</h3>
                        <p className="text-sm text-base-content/70">
                          O navegador não conseguiu exibir o PDF
                        </p>
                      </div>
                      <a
                        href={answerSheetUrl}
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
                  src={answerSheetUrl}
                  className="w-full h-full border-0"
                  title="Answer Sheet Preview"
                  onLoad={() => {
                    console.log('Cartão resposta carregado com sucesso no iframe');
                  }}
                  onError={(e) => {
                    console.error('Erro ao carregar cartão resposta:', e);
                    onPdfLoadError();
                  }}
                />
              )
            ) : (
              <div className="flex items-center justify-center h-full p-8">
                <div className="card bg-base-100 shadow-xl max-w-md">
                  <div className="card-body text-center space-y-4">
                    <ClipboardList className="w-16 h-16 mx-auto text-base-content/30" />
                    <div>
                      <h3 className="text-lg font-bold mb-2">Aguardando conteúdo</h3>
                      <p className="text-sm text-base-content/70">
                        {isCompiling
                          ? 'Gerando cartão resposta...'
                          : 'Digite no editor para gerar o cartão resposta'}
                      </p>
                    </div>
                    {isCompiling && (
                      <progress className="progress progress-info w-56"></progress>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
