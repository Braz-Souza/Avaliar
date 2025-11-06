/**
 * Custom hook for managing LaTeX compilation
 */

import { useState, useEffect } from 'react';
import LaTeXCompiler from '../services/tex';

export function useLatexCompiler(latexContent: string, autoCompile: boolean = true) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isCompiling, setIsCompiling] = useState(false);
  const [compilationError, setCompilationError] = useState<string | null>(null);
  const [pdfLoadError, setPdfLoadError] = useState(false);

  const handleCompile = async () => {
    setIsCompiling(true);
    setCompilationError(null);

    try {
      console.log('Iniciando compilação...');
      const result = await LaTeXCompiler.compileToPDF(latexContent);
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
    LaTeXCompiler.downloadLaTeX(latexContent);
  };

  // Auto-compile when content changes (debounced)
  useEffect(() => {
    if (!autoCompile) return;

    const timer = setTimeout(() => {
      if (latexContent.trim()) {
        handleCompile();
      }
    }, 1000);

    return () => clearTimeout(timer);
  }, [latexContent, autoCompile]);

  // Reset PDF load error when URL changes
  useEffect(() => {
    setPdfLoadError(false);
  }, [pdfUrl]);

  return {
    pdfUrl,
    isCompiling,
    compilationError,
    pdfLoadError,
    setPdfLoadError,
    handleCompile,
    handleDownloadPDF,
    handleDownloadLatex,
  };
}
