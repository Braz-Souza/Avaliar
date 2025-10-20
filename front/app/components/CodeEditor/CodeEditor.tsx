/**
 * CodeEditor Component
 * Syntax-highlighted code editor with overlay technique
 */

import { useRef } from 'react';
import { highlightSyntax } from '../../utils/syntax-highlighter';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function CodeEditor({ value, onChange, placeholder }: CodeEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  return (
    <div className="relative flex-1 overflow-hidden bg-white">
      <div className="absolute inset-0 p-4 font-mono text-sm overflow-auto pointer-events-none whitespace-pre-wrap leading-6 z-0">
        <div dangerouslySetInnerHTML={{ __html: highlightSyntax(value) }} />
      </div>
      <textarea
        ref={textareaRef}
        className="absolute inset-0 w-full h-full font-mono text-sm resize-none z-10 bg-transparent text-transparent caret-gray-900 border-0 p-4 leading-6 focus:outline-none"
        placeholder={placeholder || "Digite suas questões aqui..."}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        spellCheck={false}
      />
    </div>
  );
}
