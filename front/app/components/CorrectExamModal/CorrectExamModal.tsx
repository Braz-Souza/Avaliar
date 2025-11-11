/**
 * CorrectExamModal Component
 * Modal for uploading and correcting exam answer sheets using OpenCV
 */

import { useState, useRef, type RefObject } from 'react';
import { CheckCircle2, XCircle, Circle, Upload, FileCheck, AlertCircle } from 'lucide-react';
import { examCorrectorApi, type ExamCorrectionResult, type QuestionDetail } from '../../services/api';
import type { Question } from '../../types/question';

interface CorrectExamModalProps {
  dialogRef: RefObject<HTMLDialogElement | null>;
  questions: Question[];
  onClose: () => void;
}

export function CorrectExamModal({ dialogRef, questions, onClose }: CorrectExamModalProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<ExamCorrectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Extract answer key from questions
  const getAnswerKey = (): string[] => {
    return questions.map((question) => {
      const correctOption = question.options.find((opt) => opt.isCorrect);
      if (!correctOption) return 'A'; // Default if no correct answer

      // Get option index (A, B, C, D, E)
      const index = question.options.indexOf(correctOption);
      return String.fromCharCode(65 + index); // 65 is 'A' in ASCII
    });
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Por favor, selecione uma imagem válida (JPG, PNG, etc)');
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('Imagem muito grande. Tamanho máximo: 10MB');
        return;
      }

      setSelectedFile(file);
      setError(null);
      setResult(null);

      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const file = event.dataTransfer.files?.[0];

    if (file) {
      // Simulate file input change
      const input = fileInputRef.current;
      if (input) {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        input.files = dataTransfer.files;
        handleFileSelect({ target: input } as any);
      }
    }
  };

  const handleCorrect = async () => {
    if (!selectedFile) {
      setError('Por favor, selecione uma imagem do cartão resposta');
      return;
    }

    if (questions.length === 0) {
      setError('Nenhuma questão encontrada na prova');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const answerKey = getAnswerKey();
      const numOptions = Math.max(...questions.map(q => q.options.length));

      const correctionResult = await examCorrectorApi.correct(
        selectedFile,
        answerKey,
        questions.length,
        numOptions
      );

      setResult(correctionResult);
    } catch (err: any) {
      console.error('Erro ao corrigir prova:', err);
      setError(
        err.response?.data?.detail ||
        'Erro ao processar imagem. Verifique se o cartão resposta está legível.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    onClose();
  };

  const getStatusIcon = (detail: QuestionDetail) => {
    switch (detail.status) {
      case 'correct':
        return <CheckCircle2 className="w-5 h-5 text-success" />;
      case 'wrong':
        return <XCircle className="w-5 h-5 text-error" />;
      case 'blank':
        return <Circle className="w-5 h-5 text-base-content/30" />;
    }
  };

  const getStatusBadge = (detail: QuestionDetail) => {
    switch (detail.status) {
      case 'correct':
        return <div className="badge badge-success badge-sm">Correta</div>;
      case 'wrong':
        return <div className="badge badge-error badge-sm">Errada</div>;
      case 'blank':
        return <div className="badge badge-ghost badge-sm">Em branco</div>;
    }
  };

  return (
    <dialog ref={dialogRef} className="modal modal-bottom sm:modal-middle">
      <div className="modal-box max-w-4xl">
        <h3 className="font-bold text-lg flex items-center gap-2 mb-4">
          <FileCheck className="w-5 h-5" />
          Corrigir Prova Automaticamente
        </h3>

        {!result ? (
          <>
            {/* Upload Section */}
            <div className="space-y-4">
              <div className="alert alert-info">
                <AlertCircle className="w-5 h-5" />
                <div className="text-sm">
                  <p className="font-semibold">Instruções:</p>
                  <ul className="list-disc list-inside mt-1">
                    <li>Tire uma foto ou escaneie o cartão resposta</li>
                    <li>Certifique-se que a imagem está nítida e bem iluminada</li>
                    <li>O sistema detectará as marcações automaticamente</li>
                  </ul>
                </div>
              </div>

              {/* Drag and Drop Area */}
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  selectedFile
                    ? 'border-success bg-success/10'
                    : 'border-base-300 hover:border-primary hover:bg-base-200'
                }`}
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
              >
                {previewUrl ? (
                  <div className="space-y-4">
                    <img
                      src={previewUrl}
                      alt="Preview"
                      className="max-h-64 mx-auto rounded-lg shadow-lg"
                    />
                    <p className="text-sm font-medium">{selectedFile?.name}</p>
                    <button
                      className="btn btn-sm btn-outline"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      Trocar Imagem
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Upload className="w-12 h-12 mx-auto text-base-content/40" />
                    <div>
                      <p className="font-semibold mb-1">
                        Arraste a imagem aqui ou clique para selecionar
                      </p>
                      <p className="text-sm text-base-content/60">
                        Formatos: JPG, PNG (máx. 10MB)
                      </p>
                    </div>
                    <button
                      className="btn btn-primary"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      Selecionar Imagem
                    </button>
                  </div>
                )}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleFileSelect}
                />
              </div>

              {/* Info */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-base-content/60">
                  Questões na prova: <strong>{questions.length}</strong>
                </span>
                <span className="text-base-content/60">
                  Gabarito: <strong>{getAnswerKey().join(', ')}</strong>
                </span>
              </div>

              {/* Error Message */}
              {error && (
                <div className="alert alert-error">
                  <XCircle className="w-5 h-5" />
                  <span>{error}</span>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="modal-action">
              <button className="btn btn-ghost" onClick={handleClose}>
                Cancelar
              </button>
              <button
                className="btn btn-primary gap-2"
                onClick={handleCorrect}
                disabled={!selectedFile || isProcessing}
              >
                {isProcessing ? (
                  <>
                    <span className="loading loading-spinner loading-sm"></span>
                    Processando...
                  </>
                ) : (
                  <>
                    <FileCheck className="w-5 h-5" />
                    Corrigir Prova
                  </>
                )}
              </button>
            </div>
          </>
        ) : (
          <>
            {/* Results Section */}
            <div className="space-y-6">
              {/* Summary Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="stat bg-base-200 rounded-lg p-4">
                  <div className="stat-title text-xs">Total</div>
                  <div className="stat-value text-2xl">{result.total}</div>
                </div>
                <div className="stat bg-success/10 rounded-lg p-4">
                  <div className="stat-title text-xs text-success">Corretas</div>
                  <div className="stat-value text-2xl text-success">{result.correct}</div>
                </div>
                <div className="stat bg-error/10 rounded-lg p-4">
                  <div className="stat-title text-xs text-error">Erradas</div>
                  <div className="stat-value text-2xl text-error">{result.wrong}</div>
                </div>
                <div className="stat bg-base-200 rounded-lg p-4">
                  <div className="stat-title text-xs">Em Branco</div>
                  <div className="stat-value text-2xl">{result.blank}</div>
                </div>
              </div>

              {/* Score */}
              <div className="card bg-gradient-to-br from-primary to-secondary text-primary-content">
                <div className="card-body items-center text-center">
                  <h4 className="card-title text-3xl">
                    {result.score_percentage.toFixed(1)}%
                  </h4>
                  <p>
                    Nota: {result.score} / {result.total}
                  </p>
                </div>
              </div>

              {/* Detailed Results */}
              <div>
                <h4 className="font-semibold mb-3">Detalhamento por Questão</h4>
                <div className="max-h-64 overflow-y-auto space-y-2">
                  {result.details.map((detail) => (
                    <div
                      key={detail.question}
                      className={`flex items-center justify-between p-3 rounded-lg ${
                        detail.status === 'correct'
                          ? 'bg-success/10'
                          : detail.status === 'wrong'
                          ? 'bg-error/10'
                          : 'bg-base-200'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        {getStatusIcon(detail)}
                        <span className="font-medium">Questão {detail.question}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-sm">
                          <span className="text-base-content/60">Detectada: </span>
                          <strong>{detail.detected || '-'}</strong>
                          <span className="text-base-content/60 mx-2">|</span>
                          <span className="text-base-content/60">Correta: </span>
                          <strong>{detail.correct_answer}</strong>
                        </div>
                        {getStatusBadge(detail)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="modal-action">
              <button className="btn btn-primary" onClick={handleClose}>
                Fechar
              </button>
            </div>
          </>
        )}
      </div>

      {/* Backdrop - click to close */}
      <form method="dialog" className="modal-backdrop">
        <button onClick={handleClose}>close</button>
      </form>
    </dialog>
  );
}
