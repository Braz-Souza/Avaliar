/**
 * Custom hook for managing LaTeX compilation
 */

import { useState, useEffect } from 'react';
import LaTeXCompiler from '../services/tex';

export function useLatexCompiler(latexContent: string, autoCompile: boolean = true, provaTitle?: string) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isCompiling, setIsCompiling] = useState(false);
  const [compilationError, setCompilationError] = useState<string | null>(null);
  const [pdfLoadError, setPdfLoadError] = useState(false);
  const [answerSheetUrl, setAnswerSheetUrl] = useState<string | null>(null);
  const [answerSheetLoadError, setAnswerSheetLoadError] = useState(false);

  const handleCompile = async () => {
    setIsCompiling(true);
    setCompilationError(null);

    try {
      console.log('Iniciando compilação...');
      const result = await LaTeXCompiler.compileToPDF(latexContent, provaTitle);
      console.log('Resultado da compilação:', result);

      if (result.success && result.pdfUrl) {
        console.log('PDF URL gerada:', result.pdfUrl);
        console.log('Definindo pdfUrl no state...');
        setPdfUrl(result.pdfUrl);
        setPdfLoadError(false);
        console.log('PDF URL definida com sucesso');
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
    LaTeXCompiler.downloadLaTeX(latexContent, 'prova.tex', provaTitle);
  };

  const handleCompileAnswerSheet = async () => {
    setIsCompiling(true);
    setCompilationError(null);

    try {
      console.log('Compilando cartão resposta...');
      const result = await LaTeXCompiler.compileAnswerSheet(latexContent, provaTitle);
      console.log('Resultado da compilação do cartão resposta:', result);

      if (result.success && result.pdfUrl) {
        console.log('Cartão resposta URL gerada:', result.pdfUrl);
        setAnswerSheetUrl(result.pdfUrl);
        setAnswerSheetLoadError(false);
        console.log('Cartão resposta URL definida com sucesso');
      } else {
        console.error('Erro na compilação do cartão resposta:', result.error);
        setCompilationError(result.error || 'Erro desconhecido na compilação do cartão resposta');
      }
    } catch (error) {
      console.error('Erro ao compilar cartão resposta:', error);
      setCompilationError('Erro ao compilar o cartão resposta: ' + (error instanceof Error ? error.message : 'Erro desconhecido'));
    } finally {
      setIsCompiling(false);
    }
  };

  const handleDownloadAnswerSheet = () => {
    if (answerSheetUrl) {
      LaTeXCompiler.downloadPDF(answerSheetUrl);
    } else {
      handleCompileAnswerSheet();
    }
  };

  // Auto-compile when content changes (debounced)
  useEffect(() => {
    if (!autoCompile) return;

    const timer = setTimeout(() => {
      if (latexContent.trim()) {
        handleCompile();
        handleCompileAnswerSheet();
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [latexContent, autoCompile, provaTitle]);

  // Reset PDF load error when URL changes
  useEffect(() => {
    setPdfLoadError(false);
  }, [pdfUrl]);

  // Reset answer sheet load error when URL changes
  useEffect(() => {
    setAnswerSheetLoadError(false);
  }, [answerSheetUrl]);

  return {
    pdfUrl,
    isCompiling,
    compilationError,
    pdfLoadError,
    setPdfLoadError,
    handleCompile,
    handleDownloadPDF,
    handleDownloadLatex,
    answerSheetUrl,
    answerSheetLoadError,
    setAnswerSheetLoadError,
    handleCompileAnswerSheet,
    handleDownloadAnswerSheet,
  };
}
