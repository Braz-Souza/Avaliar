/**
 * Syntax highlighting for LaTeX content
 */

export function highlightSyntax(text: string): string {
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
