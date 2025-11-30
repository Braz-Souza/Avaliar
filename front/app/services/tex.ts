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

\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage[margin=2cm]{geometry}
\\usepackage{enumitem}
\\usepackage{array}

\\begin{document}

\\noindent
\\begin{tabular}{|p{0.15\\textwidth}|p{0.78\\textwidth}|}
\\hline
\\textbf{PROVA} & \\textbf{%TITLE%} \\\\
\\hline
\\end{tabular}

\\vspace{0.2cm}

\\noindent
\\begin{tabular}{|p{0.08\\textwidth}|p{0.27\\textwidth}|p{0.16\\textwidth}|p{0.16\\textwidth}|p{0.06\\textwidth}|p{0.10\\textwidth}|}
\\hline
\\end{tabular}

\\vspace{0.5cm}

`,
    question: `\\noindent\\textbf{%ID%.} %QUESTION%

\\begin{enumerate}[label=\\alph*), leftmargin=1cm, itemsep=0pt, topsep=2pt]
%CHOICES%
\\end{enumerate}

\\vspace{0.3cm}
`,
    footer: `
\\end{document}`
  };

  static generateAMCDocument(content: string, title: string = 'Avaliacao'): string {
    // Se o conteudo ja contem estrutura LaTeX completa, retorna como esta
    if (content.includes('\\documentclass') && content.includes('\\begin{document}')) {
      return content;
    }

    // Caso contrario, usa o template AMC
    const processedContent = this.processQuestionsContent(content);
    const header = this.amcTemplate.header.replace('%TITLE%', title);
    return header + processedContent + this.amcTemplate.footer;
  }

  private static processQuestionsContent(content: string): string {
    // Processa questoes simples no formato:
    // Q: Pergunta?
    // a) Opcao A
    // b) Opcao B *
    // c) Opcao C

    const lines = content.split('\n');
    let processed = '';
    let questionId = 1;
    let currentQuestion = '';
    let currentChoices: string[] = [];
    let isMultiple = false;
    const questionRegex = /^(Q)\d+:/;

    for (let line of lines) {
      line = line.trim();

      if (questionRegex.test(line)) {
        // Finaliza questao anterior se existir
        if (currentQuestion) {
          processed += this.buildQuestion(currentQuestion, currentChoices, isMultiple, questionId++);
          currentChoices = [];
        }

        isMultiple = line.startsWith('QM:');
        currentQuestion = line.replace(/^(Q)\d+:\s*/, '').trim();
      } else if (line.match(/^[a-z]\)/)) {
        // Opcao de resposta
        const isCorrect = line.includes('*');
        const optionText = line.replace(/^[a-z]\)/, '').replace('*', '').trim();

        // Adiciona marcacao de resposta correta como comentario
        if (isCorrect) {
          currentChoices.push(`  \\item ${optionText} % CORRECT`)
        } else {
          currentChoices.push(`  \\item ${optionText}`)
        }
      } else if (line && !line.startsWith('%')) {
        // Texto adicional ou conteudo LaTeX direto
        processed += line + '\n';
      }
    }

    // Finaliza ultima questao
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
      .replace('%CHOICES%', choices.join('\n')) + '\n';
  }

  static async compileToTeX(content: string, title?: string): Promise<string> {
    return this.generateAMCDocument(content, title);
  }

  static async compileToPDF(content: string, title?: string): Promise<CompilationResult> {
    try {
      const latexContent = this.generateAMCDocument(content, title);

      // Importa configuracao da API
      const { API_CONFIG, getResourceUrl } = await import('../config/api');

      // Obtem o token do localStorage
      const token = localStorage.getItem('auth_token');

      console.log('Enviando requisicao de compilacao para:', `${API_CONFIG.baseURL}/latex/compile`);

      const response = await fetch(`${API_CONFIG.baseURL}/latex/compile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          latex: latexContent,
          filename: this.sessionId
        }),
      });

      console.log('Resposta recebida:', response.status, response.statusText);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Dados da resposta JSON:', result);

      if (result.success) {
        const originalUrl = result.pdfUrl;
        const processedUrl = getResourceUrl(originalUrl);
        console.log('URL original do backend:', originalUrl);
        console.log('URL processada pelo getResourceUrl:', processedUrl);

        return {
          success: true,
          pdfUrl: processedUrl,
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
      console.error('Erro durante compilacao:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network or unknown error',
      };
    }
  }

  static async compileAnswerSheet(content: string, title?: string): Promise<CompilationResult> {
    try {
      const latexContent = this.generateAMCDocument(content, title);

      // Importa configuracao da API
      const { API_CONFIG, getResourceUrl } = await import('../config/api');

      // Obtem o token do localStorage
      const token = localStorage.getItem('auth_token');

      console.log('Enviando requisicao de compilacao do cartao resposta para:', `${API_CONFIG.baseURL}/latex/compile-answer-sheet`);

      const response = await fetch(`${API_CONFIG.baseURL}/latex/compile-answer-sheet`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          latex: latexContent,
          filename: 'cartao_resposta'
        }),
      });

      console.log('Resposta recebida do cartao resposta:', response.status, response.statusText);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Dados da resposta do cartao resposta:', result);

      if (result.success) {
        const originalUrl = result.pdfUrl;
        const processedUrl = getResourceUrl(originalUrl);
        console.log('URL original do cartao resposta:', originalUrl);
        console.log('URL processada do cartao resposta:', processedUrl);

        return {
          success: true,
          pdfUrl: processedUrl,
          logs: result.logs || [],
        };
      } else {
        return {
          success: false,
          error: result.error || 'Answer sheet compilation failed',
          logs: result.logs || [],
        };
      }
    } catch (error) {
      console.error('Erro durante compilacao do cartao resposta:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network or unknown error',
      };
    }
  }

  /**
   * Compila gabarito (cartão resposta com respostas corretas marcadas)
   */
  static async compileAnswerKey(content: string, title?: string): Promise<CompilationResult> {
    try {
      const latexContent = this.generateAMCDocument(content, title);

      // Importa configuracao da API
      const { API_CONFIG, getResourceUrl } = await import('../config/api');

      // Obtem o token do localStorage
      const token = localStorage.getItem('auth_token');

      console.log('Enviando requisicao de compilacao do gabarito para:', `${API_CONFIG.baseURL}/latex/compile-answer-key`);

      const response = await fetch(`${API_CONFIG.baseURL}/latex/compile-answer-key`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          latex: latexContent,
          filename: 'gabarito'
        }),
      });

      console.log('Resposta recebida do gabarito:', response.status, response.statusText);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Dados da resposta do gabarito:', result);

      if (result.success) {
        const originalUrl = result.pdfUrl;
        const processedUrl = getResourceUrl(originalUrl);
        console.log('URL original do gabarito:', originalUrl);
        console.log('URL processada do gabarito:', processedUrl);

        return {
          success: true,
          pdfUrl: processedUrl,
          logs: result.logs || [],
        };
      } else {
        return {
          success: false,
          error: result.error || 'Answer key compilation failed',
          logs: result.logs || [],
        };
      }
    } catch (error) {
      console.error('Erro durante compilacao do gabarito:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network or unknown error',
      };
    }
  }

  static downloadLaTeX(content: string, filename: string = 'prova.tex', title?: string): void {
    const latexContent = this.generateAMCDocument(content, title);
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
