
import { ArrowLeft, Download, FileText, Eye, ExternalLink, Save, FolderOpen } from "lucide-react";
import { NavLink, useSearchParams } from "react-router";
import { useState, useRef, useEffect } from "react";
import LaTeXCompiler from "../services/tex";
import { provasApi } from "../services/api";
import type { Route } from "./+types/prova";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Prova" },
    { name: "description", content: "Plataforma web completa para criação, gestão e aplicação de provas educacionais" },
  ];
}

function highlightSyntax(text: string): string {
  if (!text) return '';

  return text
    // Questões
    .replace(/^(Q:|QM:)(.*)$/gm, '<span class="text-blue-600 font-semibold">$1</span><span class="text-gray-800">$2</span>')
    // Opções de resposta
    .replace(/^([a-z]\))\s*(.*)(\*?)$/gm, (match, option, content, asterisk) => {
      if (asterisk) {
        return `<span class="text-green-600 font-medium">${option}</span> <span class="text-green-700">${content}</span><span class="text-green-500 font-bold"> ${asterisk}</span>`;
      } else {
        return `<span class="text-purple-600">${option}</span> <span class="text-gray-700">${content}</span>`;
      }
    })
    // Comandos LaTeX
    .replace(/\\([a-zA-Z]+)(\{[^}]*\})?/g, '<span class="text-red-600">\\$1</span><span class="text-red-400">$2</span>')
    // Comentários
    .replace(/^(%.*$)/gm, '<span class="text-gray-400 italic">$1</span>')
    // Quebras de linha
    .replace(/\n/g, '\n');
}

export default function Prova() {
  const [searchParams] = useSearchParams();
  const provaId = searchParams.get('id');
  
  const [latexContent, setLatexContent] = useState(`Q: Qual é a capital do Brasil?
a) São Paulo
b) Brasília *
c) Rio de Janeiro
d) Belo Horizonte

QM: Quais das seguintes são linguagens de programação?
a) JavaScript *
b) HTML
c) Python *
d) CSS`);

  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isCompiling, setIsCompiling] = useState(false);
  const [compilationError, setCompilationError] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState<'pdf' | 'latex'>('pdf');
  const [pdfLoadError, setPdfLoadError] = useState(false);
  const [provaName, setProvaName] = useState<string>('');
  const [currentProvaId, setCurrentProvaId] = useState<string | null>(provaId);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const saveDialogRef = useRef<HTMLDialogElement>(null);

  const handleCompile = async () => {
    setIsCompiling(true);
    setCompilationError(null);

    try {
      console.log('Iniciando compilação...');
      const result = await LaTeXCompiler.compileToPDF(latexContent);
      console.log('Resultado da compilação:', result);

      if (result.success && result.pdfUrl) {
        console.log('PDF URL:', result.pdfUrl);
        setPdfUrl(result.pdfUrl);
        setPdfLoadError(false);
      } else {
        console.error('Erro na compilação:', result.error);
        setCompilationError(result.error || 'Erro desconhecido na compilação');
      }
    } catch (error) {
      console.error('Erro ao compilar:', error);
      setCompilationError('Erro ao compilar o documento: ' + (error instanceof Error ? error.message : 'Erro desconhecido'));
    } finally {
      setIsCompiling(false);
    }
  };

  const handleDownloadPDF = () => {
    if (pdfUrl) {
      LaTeXCompiler.downloadPDF(pdfUrl);
    } else {
      handleCompile();
    }
  };

  const handleDownloadLatex = () => {
    LaTeXCompiler.downloadLaTeX(latexContent);
  };

  const getPreviewContent = () => {
    if (previewMode === 'latex') {
      return LaTeXCompiler.generateAMCDocument(latexContent);
    }
    return null;
  };

  const handleSaveProva = async () => {
    if (!provaName.trim()) {
      setSaveError('Por favor, insira um nome para a prova');
      return;
    }

    setIsSaving(true);
    setSaveError(null);

    try {
      if (currentProvaId) {
        // Update existing prova
        await provasApi.update(currentProvaId, {
          name: provaName,
          content: latexContent,
        });
      } else {
        // Create new prova
        const result = await provasApi.create({
          name: provaName,
          content: latexContent,
        });
        setCurrentProvaId(result.id);
      }

      setShowSaveDialog(false);
      saveDialogRef.current?.close();
    } catch (error) {
      console.error('Erro ao salvar prova:', error);
      setSaveError('Erro ao salvar a prova. Tente novamente.');
    } finally {
      setIsSaving(false);
    }
  };

  const openSaveDialog = () => {
    setShowSaveDialog(true);
    setSaveError(null);
    // Open dialog after state update
    setTimeout(() => {
      saveDialogRef.current?.showModal();
    }, 0);
  };

  const closeSaveDialog = () => {
    setShowSaveDialog(false);
    setSaveError(null);
    saveDialogRef.current?.close();
  };

  // Load prova if ID is provided
  useEffect(() => {
    if (provaId) {
      provasApi.get(provaId)
        .then((prova) => {
          setLatexContent(prova.content);
          setProvaName(prova.name);
          setCurrentProvaId(provaId);
        })
        .catch((error) => {
          console.error('Erro ao carregar prova:', error);
          setCompilationError('Erro ao carregar a prova');
        });
    }
  }, [provaId]);

  useEffect(() => {
    // Auto-compile when content changes (debounced)
    const timer = setTimeout(() => {
      if (latexContent.trim()) {
        handleCompile();
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [latexContent]);

  // Reset PDF load error when URL changes
  useEffect(() => {
    setPdfLoadError(false);
  }, [pdfUrl]);

  return (
    <main className="flex items-center justify-center h-screen bg-base-200">
      <div className="flex flex-col max-w-36">
        <NavLink
          className="btn btn-primary gap-4 flex-1 p-2 m-2"
          to="/"
        >
          <ArrowLeft />
          Voltar
        </NavLink>

        <button
          className="btn btn-success flex-1 p-2 m-2 gap-2"
          onClick={openSaveDialog}
        >
          <Save className="w-4 h-4" />
          {currentProvaId ? 'Atualizar' : 'Salvar'}
        </button>

        <button
          className={`btn flex-1 p-2 m-2 gap-2 ${isCompiling ? 'btn-disabled' : 'btn-primary btn-outline'}`}
          onClick={handleDownloadPDF}
          disabled={isCompiling}
        >
          <Download className="w-4 h-4" />
          {isCompiling ? 'Compilando...' : 'Baixar PDF'}
        </button>

        <button
          className="btn btn-primary btn-outline flex-1 p-2 m-2 gap-2"
          onClick={handleDownloadLatex}
        >
          <FileText className="w-4 h-4" />
          Baixar LaTeX
        </button>

        <div className="flex flex-col gap-2 mt-4">
          <span className="text-sm font-medium">Visualização:</span>
          <div className="btn-group">
            <button
              className={`btn btn-sm ${previewMode === 'pdf' ? 'btn-active' : 'btn-outline'}`}
              onClick={() => setPreviewMode('pdf')}
            >
              PDF
            </button>
            <button
              className={`btn btn-sm ${previewMode === 'latex' ? 'btn-active' : 'btn-outline'}`}
              onClick={() => setPreviewMode('latex')}
            >
              LaTeX
            </button>
          </div>
        </div>
      </div>

      <div className="h-full w-fit bg-base-400 flex flex-1 p-8 gap-8">
        <div className="flex flex-col flex-1 h-full gap-4">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-medium">Editor</h3>
          </div>

          <div className="relative flex-1 h-full">
            <textarea
              ref={textareaRef}
              className="shadow textarea absolute inset-0 w-full h-full font-mono text-sm resize-none z-10 bg-transparent text-transparent caret-gray-900"
              placeholder=""
              value={latexContent}
              onChange={(e) => setLatexContent(e.target.value)}
              spellCheck={false}
            />
            <div className="absolute inset-0 p-3 font-mono text-sm overflow-auto pointer-events-none whitespace-pre-wrap leading-5">
              <div dangerouslySetInnerHTML={{ __html: highlightSyntax(latexContent) }} />
            </div>
            <div className="absolute bottom-2 right-2 text-xs text-gray-500 bg-white px-2 py-1 rounded shadow pointer-events-none">
              Formato: Q: pergunta / QM: múltipla / a) opção / * = correta
            </div>
          </div>

          {compilationError && (
            <div className="alert alert-error">
              <span className="text-sm">{compilationError}</span>
            </div>
          )}
        </div>

        <div className="flex flex-col flex-1 h-full gap-4">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-medium">Visualização</h3>
            {isCompiling && <span className="loading loading-spinner loading-sm"></span>}
          </div>

          <div className="bg-base-100 shadow flex flex-1 h-full w-full overflow-hidden rounded-lg">
            {previewMode === 'pdf' ? (
              pdfUrl ? (
                pdfLoadError ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <ExternalLink className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                      <p className="mb-4">Erro ao carregar PDF no navegador</p>
                      <a
                        href={pdfUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-primary btn-sm"
                      >
                        Abrir PDF em nova aba
                      </a>
                    </div>
                  </div>
                ) : (
                  <iframe
                    src={pdfUrl}
                    className="w-full h-full border-0"
                    title="PDF Preview"
                    onLoad={() => console.log('PDF carregado com sucesso')}
                    onError={() => {
                      console.error('Erro ao carregar iframe');
                      setPdfLoadError(true);
                    }}
                  >
                    <div className="flex items-center justify-center h-full">
                      <span>PDF não disponível - seu navegador não suporta visualização de PDF</span>
                    </div>
                  </iframe>
                )
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <Eye className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                    <p>Digite algo no editor para gerar o PDF</p>
                    {isCompiling && <p className="text-sm text-gray-500 mt-2">Compilando...</p>}
                  </div>
                </div>
              )
            ) : (
              <pre className="p-4 overflow-auto text-sm font-mono w-full h-full bg-gray-50">
                {getPreviewContent()}
              </pre>
            )}
          </div>
        </div>
      </div>

      {/* Save Dialog */}
      <dialog ref={saveDialogRef} className="modal">
        <div className="modal-box">
          <h3 className="font-bold text-lg mb-4">
            {currentProvaId ? 'Atualizar Prova' : 'Salvar Prova'}
          </h3>
          
          <div className="form-control w-full">
            <label className="label">
              <span className="label-text">Nome da Prova</span>
            </label>
            <input
              type="text"
              placeholder="Ex: Prova de Matemática - Unidade 1"
              className="input input-bordered w-full"
              value={provaName}
              onChange={(e) => setProvaName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSaveProva();
                }
              }}
            />
          </div>

          {saveError && (
            <div className="alert alert-error mt-4">
              <span className="text-sm">{saveError}</span>
            </div>
          )}

          <div className="modal-action">
            <button
              className="btn btn-ghost"
              onClick={closeSaveDialog}
              disabled={isSaving}
            >
              Cancelar
            </button>
            <button
              className={`btn btn-success ${isSaving ? 'loading' : ''}`}
              onClick={handleSaveProva}
              disabled={isSaving}
            >
              {isSaving ? 'Salvando...' : (currentProvaId ? 'Atualizar' : 'Salvar')}
            </button>
          </div>
        </div>
        <form method="dialog" className="modal-backdrop">
          <button onClick={closeSaveDialog}>close</button>
        </form>
      </dialog>
    </main>
  );
}