interface CompilationResult {
  success: boolean;
  pdfUrl?: string;
  error?: string;
  logs?: string[];
}

interface AMCTemplate {
  header: string;
  question: string;
  questionMultiple: string;
  footer: string;
}

export class LaTeXCompiler {
  private static sessionId: string = 'prova-session-' + Date.now();

  private static amcTemplate: AMCTemplate = {
    header: `\\documentclass[a4paper]{article}

\\usepackage[utf8x]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage[box,completemulti]{automultiplechoice}

\\begin{document}
% Remove DRAFT watermark and examination message
\\AMCtext{draft}{}
\\AMCtext{message}{}
\\def\\AMC@loc@draft{}
\\def\\AMC@loc@message{}
\\AMCrandomseed{1237893}

\\onecopy{1}{

%%% beginning of the test sheet header:
\\noindent{\\bf QCM  \\hfill PROVA}

\\vspace*{.5cm}
\\begin{minipage}{.4\\linewidth}
\\centering\\large\\bf Prova\\\\ Avaliação\\end{minipage}
\\namefield{\\fbox{
                \\begin{minipage}{.5\\linewidth}
                  Nome completo:

                  \\vspace*{.5cm}\\dotfill
                  \\vspace*{1mm}
                \\end{minipage}
         }}

\\begin{center}\\em

Campo de descrição sobre a prova...

\\end{center}
\\vspace{1ex}

%%% end of the header
`,
    question: `\\begin{question}{q%ID%}
  %QUESTION%
  \\begin{choices}
    %CHOICES%
  \\end{choices}
\\end{question}`,
    questionMultiple: `\\begin{questionmult}{qm%ID%}
  %QUESTION%
  \\begin{choices}
    %CHOICES%
  \\end{choices}
\\end{questionmult}`,
    footer: `
}
\\end{document}`
  };

  static generateAMCDocument(content: string): string {
    // Se o conteúdo já contém estrutura LaTeX completa, retorna como está
    if (content.includes('\\documentclass') && content.includes('\\begin{document}')) {
      return content;
    }

    // Caso contrário, usa o template AMC
    const processedContent = this.processQuestionsContent(content);
    return this.amcTemplate.header + processedContent + this.amcTemplate.footer;
  }

  private static processQuestionsContent(content: string): string {
    // Processa questões simples no formato:
    // Q: Pergunta?
    // a) Opção A
    // b) Opção B *
    // c) Opção C

    const lines = content.split('\n');
    let processed = '';
    let questionId = 1;
    let currentQuestion = '';
    let currentChoices: string[] = [];
    let isMultiple = false;

    for (let line of lines) {
      line = line.trim();

      if (line.startsWith('Q:') || line.startsWith('QM:')) {
        // Finaliza questão anterior se existir
        if (currentQuestion) {
          processed += this.buildQuestion(currentQuestion, currentChoices, isMultiple, questionId++);
          currentChoices = [];
        }

        isMultiple = line.startsWith('QM:');
        currentQuestion = line.substring(line.indexOf(':') + 1).trim();
      } else if (line.match(/^[a-z]\)/)) {
        // Opção de resposta
        const isCorrect = line.includes('*');
        const optionText = line.replace(/^[a-z]\)/, '').replace('*', '').trim();

        if (isCorrect) {
          currentChoices.push(`\\correctchoice{${optionText}}`);
        } else {
          currentChoices.push(`\\wrongchoice{${optionText}}`);
        }
      } else if (line && !line.startsWith('%')) {
        // Texto adicional ou conteúdo LaTeX direto
        processed += line + '\n';
      }
    }

    // Finaliza última questão
    if (currentQuestion) {
      processed += this.buildQuestion(currentQuestion, currentChoices, isMultiple, questionId);
    }

    return processed;
  }

  private static buildQuestion(question: string, choices: string[], isMultiple: boolean, id: number): string {
    const template = isMultiple ? this.amcTemplate.questionMultiple : this.amcTemplate.question;
    return template
      .replace('%ID%', id.toString())
      .replace('%QUESTION%', question)
      .replace('%CHOICES%', choices.join('\n    ')) + '\n\n';
  }

  static async compileToTeX(content: string): Promise<string> {
    return this.generateAMCDocument(content);
  }

  static async compileToPDF(content: string): Promise<CompilationResult> {
    try {
      const latexContent = this.generateAMCDocument(content);

      const response = await fetch('http://localhost:8000/api/compile-latex', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          latex: latexContent,
          filename: this.sessionId
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        return {
          success: true,
          pdfUrl: `http://localhost:8000${result.pdfUrl}`,
          logs: result.logs || [],
        };
      } else {
        return {
          success: false,
          error: result.error || 'Compilation failed',
          logs: result.logs || [],
        };
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network or unknown error',
      };
    }
  }

  static downloadLaTeX(content: string, filename: string = 'prova.tex'): void {
    const latexContent = this.generateAMCDocument(content);
    const blob = new Blob([latexContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  static downloadPDF(pdfUrl: string, filename: string = 'prova.pdf'): void {
    const a = document.createElement('a');
    a.href = pdfUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}

export default LaTeXCompiler;