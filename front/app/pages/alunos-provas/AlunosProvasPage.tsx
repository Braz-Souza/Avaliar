/**
 * Student Exams Visualization Page
 * Shows randomized exams for students with PDF export
 */

import { useState, useEffect } from "react";
import { useParams, Link } from "react-router";
import { randomizacaoApi, alunosApi, provasApi, type AlunoRandomizacaoInfo, type AlunoInfo, type ProvaInfo, type ProvaData } from "../../services/api";
import { ArrowLeft, Download, Eye, Shuffle } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";

export function AlunosProvasPage() {
  const { turmaId, provaId } = useParams<{ turmaId: string; provaId: string }>();
  const { user } = useAuth();
  const [alunos, setAlunos] = useState<AlunoRandomizacaoInfo[]>([]);
  const [alunosDetails, setAlunosDetails] = useState<{ [key: string]: AlunoInfo }>({});
  const [prova, setProva] = useState<ProvaInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [generatingPdf, setGeneratingPdf] = useState<{ [key: string]: boolean }>({});
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
            <div className="flex items-center space-x-2 text-gray-700">
              <span className="text-sm font-medium">
                {user?.name || 'Usuário'}
              </span>
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
                  <div className="stat-title">Questões por Prova</div>
                  <div className="stat-value">
                    {alunos.length > 0 ? alunos[0].questoes_order.length : 0}
                  </div>
                </div>
                <div className="stat">
                  <div className="stat-title">Randomizações</div>
                  <div className="stat-value">{alunos.length}</div>
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
              <div className="overflow-x-auto">
                <table className="table table-zebra">
                  <thead>
                    <tr>
                      <th>Aluno</th>
                      <th>Matrícula</th>
                      <th className="text-right">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {alunos.map((alunoRand) => {
                      const aluno = alunosDetails[alunoRand.aluno_id];
                      return (
                        <tr key={alunoRand.id}>
                          <td className="font-medium">
                            {aluno?.nome || 'Carregando...'}
                          </td>
                          <td>{aluno?.matricula || '-'}</td>
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
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
