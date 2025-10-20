
import { ArrowLeft, Download, FileText, Eye, ExternalLink, Save, Plus, Trash2, Check, Edit2, Code } from "lucide-react";
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

interface QuestionOption {
  id: string;
  text: string;
  isCorrect: boolean;
}

interface Question {
  id: string;
  type: 'simple' | 'multiple';
  text: string;
  options: QuestionOption[];
}

function parseLatexToQuestions(latex: string): Question[] {
  const questions: Question[] = [];
  const lines = latex.split('\n');
  let currentQuestion: Question | null = null;
  let optionIndex = 0;

  for (const line of lines) {
    const trimmed = line.trim();
    
    if (trimmed.startsWith('Q:')) {
      if (currentQuestion) questions.push(currentQuestion);
      currentQuestion = {
        id: Date.now().toString() + Math.random(),
        type: 'simple',
        text: trimmed.substring(2).trim(),
        options: [],
      };
      optionIndex = 0;
    } else if (trimmed.startsWith('QM:')) {
      if (currentQuestion) questions.push(currentQuestion);
      currentQuestion = {
        id: Date.now().toString() + Math.random(),
        type: 'multiple',
        text: trimmed.substring(3).trim(),
        options: [],
      };
      optionIndex = 0;
    } else if (trimmed.match(/^[a-z]\)/)) {
      if (currentQuestion) {
        const hasAsterisk = trimmed.endsWith('*');
        const text = trimmed.substring(2).trim().replace(/\*$/, '').trim();
        currentQuestion.options.push({
          id: Date.now().toString() + optionIndex++,
          text,
          isCorrect: hasAsterisk,
        });
      }
    }
  }

  if (currentQuestion) questions.push(currentQuestion);
  return questions;
}

function questionsToLatex(questions: Question[]): string {
  return questions.map(q => {
    const prefix = q.type === 'simple' ? 'Q:' : 'QM:';
    const questionLine = `${prefix} ${q.text}`;
    const optionLines = q.options.map((opt, idx) => {
      const letter = String.fromCharCode(97 + idx);
      const asterisk = opt.isCorrect ? ' *' : '';
      return `${letter}) ${opt.text}${asterisk}`;
    }).join('\n');
    return `${questionLine}\n${optionLines}`;
  }).join('\n\n');
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
  
  const initialLatex = `Q: Qual é a capital do Brasil?
a) São Paulo
b) Brasília *
c) Rio de Janeiro
d) Belo Horizonte

QM: Quais das seguintes são linguagens de programação?
a) JavaScript *
b) HTML
c) Python *
d) CSS`;

  const [latexContent, setLatexContent] = useState(initialLatex);
  const [questions, setQuestions] = useState<Question[]>(() => parseLatexToQuestions(initialLatex));
  const [editMode, setEditMode] = useState<'visual' | 'code'>('visual');

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

  // Sync questions with latex content
  useEffect(() => {
    if (editMode === 'visual') {
      const newLatex = questionsToLatex(questions);
      setLatexContent(newLatex);
    }
  }, [questions, editMode]);

  // Update questions when switching from code to visual mode
  useEffect(() => {
    if (editMode === 'visual') {
      const parsed = parseLatexToQuestions(latexContent);
      if (JSON.stringify(parsed) !== JSON.stringify(questions)) {
        setQuestions(parsed);
      }
    }
  }, [editMode]);

  const addQuestion = (type: 'simple' | 'multiple') => {
    const newQuestion: Question = {
      id: Date.now().toString() + Math.random(),
      type,
      text: '',
      options: [
        { id: Date.now().toString() + '0', text: '', isCorrect: false },
        { id: Date.now().toString() + '1', text: '', isCorrect: false },
      ],
    };
    setQuestions([...questions, newQuestion]);
  };

  const removeQuestion = (id: string) => {
    setQuestions(questions.filter(q => q.id !== id));
  };

  const updateQuestion = (id: string, text: string) => {
    setQuestions(questions.map(q => q.id === id ? { ...q, text } : q));
  };

  const addOption = (questionId: string) => {
    setQuestions(questions.map(q => {
      if (q.id === questionId) {
        return {
          ...q,
          options: [...q.options, {
            id: Date.now().toString() + Math.random(),
            text: '',
            isCorrect: false,
          }],
        };
      }
      return q;
    }));
  };

  const removeOption = (questionId: string, optionId: string) => {
    setQuestions(questions.map(q => {
      if (q.id === questionId) {
        return {
          ...q,
          options: q.options.filter(opt => opt.id !== optionId),
        };
      }
      return q;
    }));
  };

  const updateOption = (questionId: string, optionId: string, text: string) => {
    setQuestions(questions.map(q => {
      if (q.id === questionId) {
        return {
          ...q,
          options: q.options.map(opt => 
            opt.id === optionId ? { ...opt, text } : opt
          ),
        };
      }
      return q;
    }));
  };

  const toggleOptionCorrect = (questionId: string, optionId: string) => {
    setQuestions(questions.map(q => {
      if (q.id === questionId) {
        if (q.type === 'simple') {
          // For simple questions, only one option can be correct
          return {
            ...q,
            options: q.options.map(opt => ({
              ...opt,
              isCorrect: opt.id === optionId,
            })),
          };
        } else {
          // For multiple choice, toggle the option
          return {
            ...q,
            options: q.options.map(opt => 
              opt.id === optionId ? { ...opt, isCorrect: !opt.isCorrect } : opt
            ),
          };
        }
      }
      return q;
    }));
  };

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
          setQuestions(parseLatexToQuestions(prova.content));
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
    <main className="flex h-screen bg-gradient-to-br from-base-200 to-base-300">
      {/* Sidebar */}
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
              onClick={openSaveDialog}
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
                onClick={() => setPreviewMode('pdf')}
              >
                <Eye className="w-5 h-5" />
                <span className="flex-1 text-left">Pré-visualizar PDF</span>
              </button>
              <button
                className={`btn w-full gap-2 justify-start ${
                  previewMode === 'latex' ? 'btn-primary' : 'btn-ghost'
                }`}
                onClick={() => setPreviewMode('latex')}
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
                onClick={handleDownloadPDF}
                disabled={isCompiling}
              >
                <Download className="w-5 h-5" />
                <span className="flex-1 text-left">
                  {isCompiling ? 'Compilando...' : 'Baixar PDF'}
                </span>
              </button>
              <button
                className="btn btn-outline btn-secondary w-full gap-2 justify-start"
                onClick={handleDownloadLatex}
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

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Editor Panel */}
        <div className="flex-1 flex flex-col p-6 overflow-hidden">
          <div className="card bg-base-100 shadow-xl flex-1 flex flex-col overflow-hidden border border-base-300">
            <div className="card-body p-0 flex-1 flex flex-col overflow-hidden">
              {/* Editor Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-base-300 bg-gradient-to-r from-info/10 to-primary/10">
                <div className="flex items-center gap-2">
                  <div className="avatar placeholder">
                    <div className="bg-info text-info-content rounded-full w-8">
                      <FileText className="w-4 h-4 m-2" />
                    </div>
                  </div>
                  <h2 className="text-lg font-semibold">Editor</h2>
                </div>
                <div className="flex gap-2">
                  <button
                    className={`btn btn-sm gap-2 ${editMode === 'visual' ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setEditMode('visual')}
                  >
                    <Edit2 className="w-4 h-4" />
                    Visual
                  </button>
                  <button
                    className={`btn btn-sm gap-2 ${editMode === 'code' ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setEditMode('code')}
                  >
                    <Code className="w-4 h-4" />
                    Código
                  </button>
                </div>
              </div>

              {/* Editor Content */}
              {editMode === 'visual' ? (
                <div className="flex-1 overflow-auto p-6 bg-base-200 space-y-4">
                  {/* Questions List */}
                  {questions.length === 0 && (
                    <div className="card bg-base-100 shadow-xl">
                      <div className="card-body text-center py-12">
                        <FileText className="w-16 h-16 mx-auto text-base-content/30 mb-4" />
                        <h3 className="text-lg font-bold mb-2">Nenhuma questão adicionada</h3>
                        <p className="text-sm text-base-content/70">
                          Clique nos botões abaixo para adicionar sua primeira questão
                        </p>
                      </div>
                    </div>
                  )}

                  {questions.map((question, qIndex) => (
                    <div key={question.id} className="card bg-base-100 shadow-xl">
                      <div className="card-body">
                        {/* Question Header */}
                        <div className="flex items-start gap-3 mb-4">
                          <div className="badge badge-lg badge-primary">
                            {qIndex + 1}
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
                              onChange={(e) => updateQuestion(question.id, e.target.value)}
                              rows={2}
                            />
                          </div>
                          <button
                            className="btn btn-ghost btn-sm text-error"
                            onClick={() => removeQuestion(question.id)}
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
                                onChange={(e) => updateOption(question.id, option.id, e.target.value)}
                              />
                              <button
                                className={`btn btn-sm ${
                                  option.isCorrect 
                                    ? 'btn-success' 
                                    : 'btn-ghost'
                                }`}
                                onClick={() => toggleOptionCorrect(question.id, option.id)}
                                title={option.isCorrect ? 'Resposta correta' : 'Marcar como correta'}
                              >
                                <Check className="w-4 h-4" />
                              </button>
                              {question.options.length > 2 && (
                                <button
                                  className="btn btn-ghost btn-sm text-error"
                                  onClick={() => removeOption(question.id, option.id)}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              )}
                            </div>
                          ))}
                          
                          {/* Add Option Button */}
                          <button
                            className="btn btn-ghost btn-sm gap-2 ml-8"
                            onClick={() => addOption(question.id)}
                          >
                            <Plus className="w-3 h-3" />
                            Adicionar opção
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}

                  {/* Add Question Buttons - Below all questions */}
                  <div className="flex gap-3 pt-2">
                    <button
                      className="btn btn-primary btn-lg gap-2 flex-1 shadow-lg"
                      onClick={() => addQuestion('simple')}
                    >
                      <Plus className="w-5 h-5" />
                      Adicionar Questão Simples
                    </button>
                    <button
                      className="btn btn-secondary btn-lg gap-2 flex-1 shadow-lg"
                      onClick={() => addQuestion('multiple')}
                    >
                      <Plus className="w-5 h-5" />
                      Adicionar Múltipla Escolha
                    </button>
                  </div>
                </div>
              ) : (
                <div className="relative flex-1 overflow-hidden bg-white">
                  <div className="absolute inset-0 p-4 font-mono text-sm overflow-auto pointer-events-none whitespace-pre-wrap leading-6 z-0">
                    <div dangerouslySetInnerHTML={{ __html: highlightSyntax(latexContent) }} />
                  </div>
                  <textarea
                    ref={textareaRef}
                    className="absolute inset-0 w-full h-full font-mono text-sm resize-none z-10 bg-transparent text-transparent caret-gray-900 border-0 p-4 leading-6 focus:outline-none"
                    placeholder="Digite suas questões aqui..."
                    value={latexContent}
                    onChange={(e) => setLatexContent(e.target.value)}
                    spellCheck={false}
                  />
                </div>
              )}

              {/* Editor Footer */}
              {compilationError && (
                <div className="px-6 py-3 border-t border-base-300">
                  <div className="alert alert-error">
                    <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm">{compilationError}</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Preview Panel */}
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
                        onLoad={() => console.log('PDF carregado com sucesso')}
                        onError={() => {
                          console.error('Erro ao carregar iframe');
                          setPdfLoadError(true);
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
                      <pre className="px-6"><code className="text-sm">{getPreviewContent()}</code></pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Save Dialog */}
      <dialog ref={saveDialogRef} className="modal modal-bottom sm:modal-middle">
        <div className="modal-box">
          <h3 className="font-bold text-lg flex items-center gap-2 mb-4">
            <Save className="w-5 h-5" />
            {currentProvaId ? 'Atualizar Prova' : 'Nova Prova'}
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
              onChange={(e) => setProvaName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleSaveProva();
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
              onClick={closeSaveDialog}
              disabled={isSaving}
            >
              Cancelar
            </button>
            <button
              className={`btn btn-success gap-2 ${isSaving ? 'btn-disabled' : ''}`}
              onClick={handleSaveProva}
              disabled={isSaving}
            >
              {isSaving && <span className="loading loading-spinner loading-sm"></span>}
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