/**
 * EditorPanel Component
 * Main editor panel with visual and code modes
 */

import { FileText, Edit2, Code } from 'lucide-react';
import type { Question, EditMode } from '../../../types/question';
import { QuestionCard } from '../../../components/QuestionCard/QuestionCard';
import { CodeEditor } from '../../../components/CodeEditor/CodeEditor';
import { EmptyState } from '../../../components/EmptyState/EmptyState';
import { AddQuestionButtons } from '../../../components/AddQuestionButtons/AddQuestionButtons';

interface EditorPanelProps {
  editMode: EditMode;
  onEditModeChange: (mode: EditMode) => void;
  questions: Question[];
  latexContent: string;
  onLatexChange: (content: string) => void;
  onAddQuestion: (type: 'simple' | 'multiple') => void;
  onUpdateQuestion: (id: string, text: string) => void;
  onRemoveQuestion: (id: string) => void;
  onAddOption: (questionId: string) => void;
  onUpdateOption: (questionId: string, optionId: string, text: string) => void;
  onToggleCorrect: (questionId: string, optionId: string) => void;
  onRemoveOption: (questionId: string, optionId: string) => void;
  compilationError: string | null;
}

export function EditorPanel({
  editMode,
  onEditModeChange,
  questions,
  latexContent,
  onLatexChange,
  onAddQuestion,
  onUpdateQuestion,
  onRemoveQuestion,
  onAddOption,
  onUpdateOption,
  onToggleCorrect,
  onRemoveOption,
  compilationError,
}: EditorPanelProps) {
  return (
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
                onClick={() => onEditModeChange('visual')}
              >
                <Edit2 className="w-4 h-4" />
                Visual
              </button>
              <button
                className={`btn btn-sm gap-2 ${editMode === 'code' ? 'btn-primary' : 'btn-ghost'}`}
                onClick={() => onEditModeChange('code')}
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
              {questions.length === 0 && <EmptyState />}

              {questions.map((question, qIndex) => (
                <QuestionCard
                  key={question.id}
                  question={question}
                  index={qIndex}
                  onUpdateQuestion={onUpdateQuestion}
                  onRemoveQuestion={onRemoveQuestion}
                  onUpdateOption={onUpdateOption}
                  onToggleCorrect={onToggleCorrect}
                  onRemoveOption={onRemoveOption}
                  onAddOption={onAddOption}
                />
              ))}

              {/* Add Question Buttons */}
              <AddQuestionButtons
                onAddSimple={() => onAddQuestion('simple')}
                onAddMultiple={() => onAddQuestion('multiple')}
              />
            </div>
          ) : (
            <CodeEditor
              value={latexContent}
              onChange={onLatexChange}
            />
          )}

          {/* Editor Footer - Error Display */}
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
  );
}
