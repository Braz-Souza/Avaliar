/**
 * CodeEditor Component
 * Simple code editor for LaTeX content
 */

import { useRef } from 'react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function CodeEditor({ value, onChange, placeholder }: CodeEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  return (
    <div className="flex-1 overflow-hidden bg-white">
      <textarea
        ref={textareaRef}
        className="w-full h-full font-mono text-sm resize-none bg-white text-gray-900 border-0 p-4 leading-6 focus:outline-none"
        placeholder={placeholder || "Digite suas questões aqui..."}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        spellCheck={false}
      />
    </div>
  );
}
