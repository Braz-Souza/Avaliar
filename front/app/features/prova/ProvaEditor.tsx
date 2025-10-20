/**
 * Main Prova Editor Page Component
 * Uses clean architecture with separated concerns
 */

import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router';
import type { Route } from '../../prova/+types/prova';
import type { PreviewMode } from '../../types/question';
import { useProvaEditor } from '../../hooks/useProvaEditor';
import { useLatexCompiler } from '../../hooks/useLatexCompiler';
import { useProvaSave } from '../../hooks/useProvaSave';
import { provasApi } from '../../services/api';
import { Sidebar } from './components/Sidebar';
import { EditorPanel } from './components/EditorPanel';
import { PreviewPanel } from './components/PreviewPanel';
import { SaveDialog } from '../../components/SaveDialog/SaveDialog';

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Prova" },
    { name: "description", content: "Plataforma web completa para criação, gestão e aplicação de provas educacionais" },
  ];
}

export default function ProvaEditor() {
  const [searchParams] = useSearchParams();
  const provaId = searchParams.get('id');
  const [previewMode, setPreviewMode] = useState<PreviewMode>('pdf');

  // Custom hooks for state management
  const editor = useProvaEditor();
  const compiler = useLatexCompiler(editor.latexContent);
  const saver = useProvaSave(provaId);

  // Load prova if ID is provided
  useEffect(() => {
    if (provaId) {
      provasApi.get(provaId)
        .then((prova) => {
          editor.setContent(prova.content);
          saver.setProvaName(prova.name);
          saver.setCurrentProvaId(provaId);
        })
        .catch((error) => {
          console.error('Erro ao carregar prova:', error);
        });
    }
  }, [provaId]);

  return (
    <main className="flex h-screen bg-gradient-to-br from-base-200 to-base-300">
      <Sidebar
        provaName={saver.provaName}
        currentProvaId={saver.currentProvaId}
        isCompiling={compiler.isCompiling}
        previewMode={previewMode}
        onPreviewModeChange={setPreviewMode}
        onSave={saver.openSaveDialog}
        onDownloadPDF={compiler.handleDownloadPDF}
        onDownloadLatex={compiler.handleDownloadLatex}
      />

      <div className="flex flex-1 overflow-hidden">
        <EditorPanel
          editMode={editor.editMode}
          onEditModeChange={editor.setEditMode}
          questions={editor.questions}
          latexContent={editor.latexContent}
          onLatexChange={editor.setLatexContent}
          onAddQuestion={editor.addQuestion}
          onUpdateQuestion={editor.updateQuestion}
          onRemoveQuestion={editor.removeQuestion}
          onAddOption={editor.addOption}
          onUpdateOption={editor.updateOption}
          onToggleCorrect={editor.toggleOptionCorrect}
          onRemoveOption={editor.removeOption}
          compilationError={compiler.compilationError}
        />

        <PreviewPanel
          previewMode={previewMode}
          pdfUrl={compiler.pdfUrl}
          pdfLoadError={compiler.pdfLoadError}
          isCompiling={compiler.isCompiling}
          latexContent={editor.latexContent}
          onPdfLoadError={() => compiler.setPdfLoadError(true)}
        />
      </div>

      <SaveDialog
        dialogRef={saver.saveDialogRef}
        provaName={saver.provaName}
        onNameChange={saver.setProvaName}
        onSave={() => saver.handleSaveProva(editor.latexContent)}
        onClose={saver.closeSaveDialog}
        isSaving={saver.isSaving}
        saveError={saver.saveError}
        isUpdate={!!saver.currentProvaId}
      />
    </main>
  );
}
