/**
 * Student Exams Visualization Page
 * Shows randomized exams for students with PDF export
 */

import { useState, useEffect } from "react";
import { useParams, Link } from "react-router";
import { randomizacaoApi, alunosApi, provasApi, imageCorrectionApi, type AlunoRandomizacaoInfo, type AlunoInfo, type ProvaInfo, type ProvaData, type ImageCorrectionResponse } from "../../services/api";
import { ArrowLeft, Download, Eye, Shuffle, PackageOpen, Upload, CheckCircle, XCircle } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";

export function AlunosProvasPage() {
  const { turmaId, provaId } = useParams<{ turmaId: string; provaId: string }>();
  const { user } = useAuth();
  const [alunos, setAlunos] = useState<AlunoRandomizacaoInfo[]>([]);
  const [alunosDetails, setAlunosDetails] = useState<{ [key: string]: AlunoInfo }>({});
  const [correcoes, setCorrecoes] = useState<{ [key: string]: ImageCorrectionResponse }>({});
  const [prova, setProva] = useState<ProvaInfo | null>(null);
  const [turmaProvaId, setTurmaProvaId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [generatingPdf, setGeneratingPdf] = useState<{ [key: string]: boolean }>({});
  const [downloadingZip, setDownloadingZip] = useState(false);
  const [downloadingCartao, setDownloadingCartao] = useState(false);
  const [downloadingGabarito, setDownloadingGabarito] = useState<{ [key: string]: boolean }>({});
  const [uploadingImage, setUploadingImage] = useState<{ [key: string]: boolean }>({});
  const [dragOverAluno, setDragOverAluno] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (turmaId && provaId) {
      loadData();
    }
  }, [turmaId, provaId]);

  const loadData = async () => {
    if (!turmaId || !provaId) return;

    try {
      setLoading(true);
      setError(null);

      // Load prova details
      const provaData = await provasApi.get(provaId);
      // Convert ProvaData to ProvaInfo by adding missing fields
      const provaInfo: ProvaInfo = {
        id: provaId,
        name: provaData.name,
        created_at: new Date().toISOString(),
        modified_at: new Date().toISOString()
      };
      setProva(provaInfo);

      // Load turma-prova link to get turma-prova ID
      const turmaProvas = await randomizacaoApi.listTurmasProvas({
        turma_id: turmaId,
        prova_id: provaId
      });

      if (turmaProvas.length === 0) {
        setError('Vínculo entre turma e prova não encontrado');
        return;
      }

      const turmaProvaId = turmaProvas[0].id;
      setTurmaProvaId(turmaProvaId);

      // Load alunos randomizacoes
      const randomizacoes = await randomizacaoApi.getAlunosRandomizacoes(turmaProvaId);
      setAlunos(randomizacoes);

      // Load detailed info for each aluno
      const alunosDetailsMap: { [key: string]: AlunoInfo } = {};
      for (const rand of randomizacoes) {
        try {
          const alunoDetail = await alunosApi.get(rand.aluno_id);
          alunosDetailsMap[rand.aluno_id] = alunoDetail;
        } catch (err) {
          console.error('Erro ao carregar detalhes do aluno:', err);
        }
      }
      setAlunosDetails(alunosDetailsMap);

      // Load correções para a turma e prova
      try {
        const correcoesData = await imageCorrectionApi.getCorrecoesByTurmaProva(turmaId, provaId);
        const correcoesMap: { [key: string]: ImageCorrectionResponse } = {};
        correcoesData.forEach(correcao => {
          correcoesMap[correcao.aluno_id] = correcao;
        });
        setCorrecoes(correcoesMap);
      } catch (err) {
        console.error('Erro ao carregar correções:', err);
        // Não é um erro crítico, continuar sem as correções
      }

    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      setError('Erro ao carregar dados dos alunos');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePdf = async (alunoId: string, alunoName: string) => {
    if (!provaId) return;

    try {
      setGeneratingPdf(prev => ({ ...prev, [alunoId]: true }));

      // Download PDF blob from the new endpoint
      const pdfBlob = await randomizacaoApi.downloadAlunoProvaPdf(alunoId, provaId);

      // Create download link from blob
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `prova_${alunoName.replace(/\s+/g, '_')}_${prova?.name?.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up the URL object
      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error('Erro ao gerar PDF:', err);
      alert('Erro ao gerar PDF da prova');
    } finally {
      setGeneratingPdf(prev => ({ ...prev, [alunoId]: false }));
    }
  };

  const handleDownloadAllZip = async () => {
    if (!turmaProvaId) return;

    try {
      setDownloadingZip(true);

      const zipBlob = await randomizacaoApi.downloadAllProvasZip(turmaProvaId);

      const url = window.URL.createObjectURL(zipBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `provas_${prova?.name?.replace(/\s+/g, '_')}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error('Erro ao baixar ZIP:', err);
      alert('Erro ao baixar arquivo ZIP com todas as provas');
    } finally {
      setDownloadingZip(false);
    }
  };

  const handleDownloadCartaoResposta = async () => {
    try {
      setDownloadingCartao(true);

      // Chama o endpoint do backend diretamente
      const token = localStorage.getItem('auth_token');

      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/latex/compile-answer-sheet`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success || !result.pdfUrl) {
        throw new Error(result.error || 'Erro ao gerar cartão resposta');
      }

      // Construir a URL completa do PDF
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const pdfUrl = result.pdfUrl.startsWith('http')
        ? result.pdfUrl
        : `${baseUrl}${result.pdfUrl}`;

      // Baixar o PDF da URL gerada
      const pdfResponse = await fetch(pdfUrl, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      const pdfBlob = await pdfResponse.blob();

      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'cartao_resposta.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error('Erro ao baixar cartão resposta:', err);
      alert('Erro ao baixar cartão resposta');
    } finally {
      setDownloadingCartao(false);
    }
  };

  const handleDownloadGabarito = async (alunoId: string, alunoName: string) => {
    if (!provaId) return;

    try {
      setDownloadingGabarito(prev => ({ ...prev, [alunoId]: true }));

      const pdfBlob = await randomizacaoApi.downloadGabaritoAluno(alunoId, provaId);

      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `gabarito_${alunoName.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error('Erro ao baixar gabarito:', err);
      alert('Erro ao baixar gabarito do aluno');
    } finally {
      setDownloadingGabarito(prev => ({ ...prev, [alunoId]: false }));
    }
  };

  const handleImageUpload = async (alunoId: string, file: File) => {
    if (!turmaId || !provaId) {
      alert('❌ Erro: turmaId ou provaId não encontrado');
      return;
    }

    try {
      setUploadingImage(prev => ({ ...prev, [alunoId]: true }));

      // Validar se é uma imagem
      if (!file.type.startsWith('image/')) {
        alert('Por favor, envie apenas arquivos de imagem');
        return;
      }

      // Upload e processar imagem com os IDs necessários
      const result = await imageCorrectionApi.uploadAndProcess(
        file,
        alunoId,
        turmaId,
        provaId
      );

      // Formatar resultados da correção
      let correctionResults = '✅ Correção Salva com Sucesso!\n';
      correctionResults += '═══════════════════════════\n\n';
      correctionResults += `📊 Total de questões: ${result.total_questoes}\n`;
      correctionResults += `📝 Respostas detectadas: ${result.respostas.length}\n\n`;
      correctionResults += 'Respostas marcadas:\n';
      correctionResults += '─────────────────────\n';

      // Ordenar as questões numericamente
      const sortedRespostas = result.respostas
        .sort((a, b) => a.questao_numero - b.questao_numero);

      sortedRespostas.forEach((resposta) => {
        correctionResults += `Questão ${resposta.questao_numero}: ${resposta.resposta_marcada}\n`;
      });

      alert(correctionResults.trim());

      // Recarregar as correções após o upload
      if (turmaId && provaId) {
        try {
          const correcoesData = await imageCorrectionApi.getCorrecoesByTurmaProva(turmaId, provaId);
          const correcoesMap: { [key: string]: ImageCorrectionResponse } = {};
          correcoesData.forEach(correcao => {
            correcoesMap[correcao.aluno_id] = correcao;
          });
          setCorrecoes(correcoesMap);
        } catch (err) {
          console.error('Erro ao recarregar correções:', err);
        }
      }

    } catch (err: any) {
      console.error('Erro ao processar imagem:', err);
      const errorMessage = err.response?.data?.detail || 'Erro ao processar imagem';
      alert(`❌ ${errorMessage}`);
    } finally {
      setUploadingImage(prev => ({ ...prev, [alunoId]: false }));
    }
  };

  const handleDragOver = (e: React.DragEvent, alunoId: string) => {
    e.preventDefault();
    e.stopPropagation();

    // Não permitir drag over se já existe correção
    if (correcoes[alunoId]) {
      return;
    }

    setDragOverAluno(alunoId);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOverAluno(null);
  };

  const handleDrop = async (e: React.DragEvent, alunoId: string) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOverAluno(null);

    // Não permitir drop se já existe correção
    if (correcoes[alunoId]) {
      alert('❌ Este aluno já possui uma correção cadastrada!');
      return;
    }

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      await handleImageUpload(alunoId, files[0]);
    }
  };

  const getQuestionOrderDescription = (questoesOrder: number[]) => {
    return questoesOrder.map((originalIndex, displayPosition) =>
      `Questão ${displayPosition + 1} (original: ${originalIndex + 1})`
    ).join(', ');
  };

  const getAlternativasOrderDescription = (alternativasOrder: { [key: string]: number[] }, questaoId: string) => {
    const order = alternativasOrder[questaoId];
    if (!order || order.length === 0) return 'Nenhuma alternativa';

    return order.map((originalIndex, displayPosition) =>
      `${String.fromCharCode(65 + displayPosition)} (original: ${String.fromCharCode(65 + originalIndex)})`
    ).join(', ');
  };

  if (loading) {
    return (
      <main className="flex flex-col min-h-screen bg-base-200">
        <div className="flex-1 flex justify-center items-center">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex flex-col min-h-screen bg-base-200">
        <div className="flex-1 flex justify-center items-center">
          <div className="text-center">
            <div className="alert alert-error mb-4 max-w-md">
              <span>{error}</span>
            </div>
            <Link to="/turmas" className="btn btn-primary">
              Voltar para Turmas
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="flex flex-col min-h-screen bg-base-200">
      <header className="w-full bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link to="/turmas" className="text-gray-600 hover:text-gray-900">
                <ArrowLeft className="w-4 h-4 inline mr-2" />
                Voltar para Turmas
              </Link>
              <div>
                <h1 className="text-xl font-semibold">Provas dos Alunos</h1>
                <p className="text-sm text-gray-600">
                  {prova?.name} - {alunos.length} aluno(s)
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                className={`btn btn-secondary gap-2 ${downloadingCartao ? 'loading' : ''}`}
                onClick={handleDownloadCartaoResposta}
                disabled={downloadingCartao}
                title="Baixar cartão resposta em PDF"
              >
                {downloadingCartao ? (
                  <>
                    <span className="loading loading-spinner loading-sm"></span>
                    Gerando...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    Cartão Resposta
                  </>
                )}
              </button>
              <button
                className={`btn btn-primary gap-2 ${downloadingZip ? 'loading' : ''}`}
                onClick={handleDownloadAllZip}
                disabled={downloadingZip || alunos.length === 0}
                title="Baixar todas as provas em um arquivo ZIP"
              >
                {downloadingZip ? (
                  <>
                    <span className="loading loading-spinner loading-sm"></span>
                    Gerando ZIP...
                  </>
                ) : (
                  <>
                    <PackageOpen className="w-4 h-4" />
                    Baixar Todas (ZIP)
                  </>
                )}
              </button>
              <div className="text-gray-700">
                <span className="text-sm font-medium">
                  {user?.name || 'Usuário'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 p-4">
        <div className="w-full max-w-6xl mx-auto">
          <div className="card bg-base-100 shadow-xl p-6">
            <div className="mb-6">
              <div className="stats stats-horizontal bg-base-200">
                <div className="stat">
                  <div className="stat-title">Total de Alunos</div>
                  <div className="stat-value">{alunos.length}</div>
                </div>
                <div className="stat">
                  <div className="stat-title">Provas Corrigidas</div>
                  <div className="stat-value text-success">{Object.keys(correcoes).length}</div>
                </div>
                <div className="stat">
                  <div className="stat-title">Pendentes</div>
                  <div className="stat-value text-warning">{alunos.length - Object.keys(correcoes).length}</div>
                </div>
                <div className="stat">
                  <div className="stat-title">Questões por Prova</div>
                  <div className="stat-value">
                    {alunos.length > 0 ? alunos[0].questoes_order.length : 0}
                  </div>
                </div>
              </div>
            </div>

            {alunos.length === 0 ? (
              <div className="text-center py-12">
                <Eye className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600 mb-4">
                  Nenhum aluno encontrado para esta prova
                </p>
              </div>
            ) : (
              <>
                <div className="alert alert-info mb-4">
                  <Upload className="w-5 h-5" />
                  <div>
                    <div className="font-bold">Como enviar correções:</div>
                    <div className="text-sm">
                      Arraste uma imagem do cartão resposta sobre a linha de um aluno para processá-la automaticamente.
                      Alunos que já possuem correção não aceitarão novos envios.
                    </div>
                  </div>
                </div>
                <div className="overflow-x-auto">
                <table className="table table-zebra">
                  <thead>
                    <tr>
                      <th>Aluno</th>
                      <th>Matrícula</th>
                      <th>Status / Nota</th>
                      <th className="text-right">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {alunos.map((alunoRand) => {
                      const aluno = alunosDetails[alunoRand.aluno_id];
                      const correcao = correcoes[alunoRand.aluno_id];
                      const isDragging = dragOverAluno === alunoRand.aluno_id;
                      const isUploading = uploadingImage[alunoRand.aluno_id];
                      const hasCorrecao = !!correcao;

                      return (
                        <tr
                          key={alunoRand.id}
                          onDragOver={(e) => !hasCorrecao && handleDragOver(e, alunoRand.aluno_id)}
                          onDragLeave={handleDragLeave}
                          onDrop={(e) => handleDrop(e, alunoRand.aluno_id)}
                          className={`
                            transition-all duration-200
                            ${isDragging && !hasCorrecao ? 'bg-primary bg-opacity-10 scale-[1.02]' : ''}
                            ${isUploading ? 'opacity-50' : ''}
                            ${hasCorrecao ? 'bg-success bg-opacity-5' : ''}
                          `}
                        >
                          <td className="font-medium">
                            <div className="flex items-center gap-2">
                              {isUploading && (
                                <span className="loading loading-spinner loading-sm"></span>
                              )}
                              {isDragging && !hasCorrecao && (
                                <Upload className="w-4 h-4 text-primary animate-bounce" />
                              )}
                              {hasCorrecao && (
                                <CheckCircle className="w-4 h-4 text-success" />
                              )}
                              {aluno?.nome || 'Carregando...'}
                            </div>
                          </td>
                          <td>{aluno?.matricula || '-'}</td>
                          <td>
                            {hasCorrecao ? (
                              <div className="flex items-center gap-2">
                                <div className="badge badge-success badge-sm">Corrigido</div>
                                <span className="text-sm font-medium">
                                  {correcao.nota?.toFixed(1) || 0} | {correcao.acertos || 0} / {correcao.total_questoes || 0}
                                </span>
                              </div>
                            ) : (
                              <div className="badge badge-warning badge-sm">Pendente</div>
                            )}
                          </td>
                          <td>
                            <div className="flex gap-2 justify-end">
                              <button
                                className="btn btn-sm btn-info btn-outline gap-2"
                                onClick={() => {
                                  // Show detailed randomization info
                                  const details = Object.entries(alunoRand.alternativas_order)
                                    .map(([questaoId, alternativas]) =>
                                      `Questão ${questaoId}: ${getAlternativasOrderDescription(alunoRand.alternativas_order, questaoId)}`
                                    )
                                    .join('\n');
                                  alert(`Randomização detalhada:\n\n${details}`);
                                }}
                              >
                                <Eye className="w-4 h-4" />
                                Detalhes
                              </button>
                              <button
                                className={`btn btn-sm btn-warning btn-outline gap-2 ${
                                  downloadingGabarito[alunoRand.aluno_id] ? 'loading' : ''
                                }`}
                                onClick={() => handleDownloadGabarito(alunoRand.aluno_id, aluno?.nome || '')}
                                disabled={downloadingGabarito[alunoRand.aluno_id]}
                                title="Baixar gabarito personalizado do aluno"
                              >
                                {downloadingGabarito[alunoRand.aluno_id] ? (
                                  <span className="loading loading-spinner loading-sm"></span>
                                ) : (
                                  <Download className="w-4 h-4" />
                                )}
                                Gabarito
                              </button>
                              <button
                                className={`btn btn-sm btn-success btn-outline gap-2 ${
                                  generatingPdf[alunoRand.aluno_id] ? 'loading' : ''
                                }`}
                                onClick={() => handleGeneratePdf(alunoRand.aluno_id, aluno?.nome || '')}
                                disabled={generatingPdf[alunoRand.aluno_id]}
                              >
                                {generatingPdf[alunoRand.aluno_id] ? (
                                  <span className="loading loading-spinner loading-sm"></span>
                                ) : (
                                  <Download className="w-4 h-4" />
                                )}
                                Exportar PDF
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              </>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
