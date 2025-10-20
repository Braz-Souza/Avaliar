/**
 * Custom hook for managing prova save operations
 */

import { useState, useRef } from 'react';
import { provasApi } from '../services/api';

export function useProvaSave(initialProvaId?: string | null, initialProvaName?: string) {
  const [provaName, setProvaName] = useState<string>(initialProvaName || '');
  const [currentProvaId, setCurrentProvaId] = useState<string | null>(initialProvaId || null);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const saveDialogRef = useRef<HTMLDialogElement>(null);

  const openSaveDialog = () => {
    setShowSaveDialog(true);
    setSaveError(null);
    setTimeout(() => {
      saveDialogRef.current?.showModal();
    }, 0);
  };

  const closeSaveDialog = () => {
    setShowSaveDialog(false);
    setSaveError(null);
    saveDialogRef.current?.close();
  };

  const handleSaveProva = async (latexContent: string) => {
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

  return {
    provaName,
    setProvaName,
    currentProvaId,
    setCurrentProvaId,
    showSaveDialog,
    saveError,
    isSaving,
    saveDialogRef,
    openSaveDialog,
    closeSaveDialog,
    handleSaveProva,
  };
}
