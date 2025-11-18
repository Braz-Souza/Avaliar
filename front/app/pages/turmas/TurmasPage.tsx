/**
 * Turmas Management Page
 * CRUD operations for turmas
 */

import { useState, useEffect } from "react";
import { Link } from "react-router";
import { turmasApi, randomizacaoApi, type TurmaInfo, type TurmaData } from "../../services/api";
import { GraduationCap, PlusCircle, Edit, Trash2, Search, Users, Link2, Eye } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";

export function TurmasPage() {
  const { user } = useAuth();
  const [turmas, setTurmas] = useState<TurmaInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterAno, setFilterAno] = useState("");
  const [filterMateria, setFilterMateria] = useState("");
  const [filterCurso, setFilterCurso] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingTurma, setEditingTurma] = useState<TurmaInfo | null>(null);
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [showProvasModal, setShowProvasModal] = useState(false);
  const [selectedTurma, setSelectedTurma] = useState<TurmaInfo | null>(null);
  const [linking, setLinking] = useState(false);

  useEffect(() => {
    loadTurmas();
  }, []);

  const loadTurmas = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (filterAno) params.ano = parseInt(filterAno);
      if (filterMateria) params.materia = filterMateria;
      if (filterCurso) params.curso = filterCurso;

      const data = await turmasApi.list(params);
      setTurmas(data);
      setError(null);
    } catch (err) {
      console.error('Erro ao carregar turmas:', err);
      setError('Erro ao carregar as turmas');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (turmaId: string, turmaName: string) => {
    if (!confirm(`Tem certeza que deseja excluir a turma "${turmaName}"?`)) {
      return;
    }

    try {
      setDeletingId(turmaId);
      await turmasApi.delete(turmaId);
      setTurmas(turmas.filter(t => t.id !== turmaId));
    } catch (err) {
      console.error('Erro ao excluir turma:', err);
      alert('Erro ao excluir a turma');
    } finally {
      setDeletingId(null);
    }
  };

  const handleCreate = async (formData: TurmaData) => {
    try {
      const newTurma = await turmasApi.create(formData);
      setTurmas([...turmas, newTurma]);
      setShowCreateModal(false);
    } catch (err) {
      console.error('Erro ao criar turma:', err);
      alert('Erro ao criar a turma');
    }
  };

  const handleUpdate = async (turmaId: string, formData: Partial<TurmaData>) => {
    try {
      const updatedTurma = await turmasApi.update(turmaId, formData);
      setTurmas(turmas.map(t => t.id === turmaId ? updatedTurma : t));
      setEditingTurma(null);
    } catch (err) {
      console.error('Erro ao atualizar turma:', err);
      alert('Erro ao atualizar a turma');
    }
  };

  const handleLinkProva = (turma: TurmaInfo) => {
    setSelectedTurma(turma);
    setShowLinkModal(true);
  };

  const handleViewProvas = (turma: TurmaInfo) => {
    setSelectedTurma(turma);
    setShowProvasModal(true);
  };

  const filteredTurmas = turmas.filter(turma => {
    const matchesSearch = turma.materia.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         turma.curso.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         turma.ano.toString().includes(searchTerm);
    return matchesSearch;
  });

  return (
    <main className="flex flex-col min-h-screen bg-base-200">
      <header className="w-full bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link to="/" className="text-gray-600 hover:text-gray-900">
                ← Voltar
              </Link>
              <h1 className="text-xl font-semibold">Gerenciar Turmas</h1>
            </div>
            <div className="flex items-center space-x-2 text-gray-700">
              <Users className="w-4 h-4" />
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
            {/* Header with actions and filters */}
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-6 space-y-4 lg:space-y-0">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="btn btn-primary gap-2"
                >
                  <PlusCircle className="w-5 h-5" />
                  Nova Turma
                </button>
              </div>

              <div className="flex flex-col sm:flex-row gap-2">
                <div className="form-control">
                  <div className="input-group">
                    <Search className="w-4 h-4" />
                    <input
                      type="text"
                      placeholder="Buscar turmas..."
                      className="input input-bordered"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>

                <select
                  className="select select-bordered"
                  value={filterAno}
                  onChange={(e) => setFilterAno(e.target.value)}
                >
                  <option value="">Todos os anos</option>
                  {Array.from({length: 10}, (_, i) => new Date().getFullYear() - i).map(ano => (
                    <option key={ano} value={ano}>{ano}</option>
                  ))}
                </select>

                <input
                  type="text"
                  placeholder="Filtrar matéria"
                  className="input input-bordered"
                  value={filterMateria}
                  onChange={(e) => setFilterMateria(e.target.value)}
                />

                <input
                  type="text"
                  placeholder="Filtrar curso"
                  className="input input-bordered"
                  value={filterCurso}
                  onChange={(e) => setFilterCurso(e.target.value)}
                />

                <button onClick={loadTurmas} className="btn btn-secondary">
                  Filtrar
                </button>
              </div>
            </div>

            {error && (
              <div className="alert alert-error mb-4">
                <span>{error}</span>
              </div>
            )}

            {loading ? (
              <div className="flex justify-center py-12">
                <span className="loading loading-spinner loading-lg"></span>
              </div>
            ) : filteredTurmas.length === 0 ? (
              <div className="text-center py-12">
                <GraduationCap className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600 mb-4">
                  {searchTerm || filterAno || filterMateria || filterCurso
                    ? 'Nenhuma turma encontrada com os filtros aplicados'
                    : 'Nenhuma turma cadastrada ainda'}
                </p>
                {!searchTerm && !filterAno && !filterMateria && !filterCurso && (
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="btn btn-primary btn-sm"
                  >
                    Criar primeira turma
                  </button>
                )}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="table table-zebra">
                  <thead>
                    <tr>
                      <th>Ano</th>
                      <th>Matéria</th>
                      <th>Curso</th>
                      <th>Período</th>
                      <th className="text-right">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTurmas.map((turma) => (
                      <tr key={turma.id}>
                        <td className="font-medium">{turma.ano}</td>
                        <td>{turma.materia}</td>
                        <td>{turma.curso}</td>
                        <td>{turma.periodo}º</td>
                        <td>
                          <div className="flex gap-2 justify-end flex-wrap">
                            <button
                              onClick={() => setEditingTurma(turma)}
                              className="btn btn-sm btn-primary btn-outline gap-2"
                            >
                              <Edit className="w-4 h-4" />
                              Editar
                            </button>
                            <button
                              className={`btn btn-sm btn-info btn-outline gap-2`}
                              onClick={() => handleLinkProva(turma)}
                            >
                              <Link2 className="w-4 h-4" />
                              Vincular Prova
                            </button>
                            <button
                              className={`btn btn-sm btn-success btn-outline gap-2`}
                              onClick={() => handleViewProvas(turma)}
                            >
                              <Eye className="w-4 h-4" />
                              Ver Provas
                            </button>
                            <button
                              className={`btn btn-sm btn-error btn-outline gap-2 ${
                                deletingId === turma.id ? 'loading' : ''
                              }`}
                              onClick={() => handleDelete(turma.id, `${turma.materia} - ${turma.curso}`)}
                              disabled={deletingId === turma.id}
                            >
                              {deletingId !== turma.id && (
                                <Trash2 className="w-4 h-4" />
                              )}
                              Excluir
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">Nova Turma</h3>
            <TurmaForm
              onSubmit={handleCreate}
              onCancel={() => setShowCreateModal(false)}
            />
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editingTurma && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">Editar Turma</h3>
            <TurmaForm
              initialData={editingTurma}
              onSubmit={(data) => handleUpdate(editingTurma.id, data)}
              onCancel={() => setEditingTurma(null)}
            />
          </div>
        </div>
      )}

      {/* Link Prova Modal */}
      {showLinkModal && selectedTurma && (
        <LinkProvaModal
          turma={selectedTurma}
          onLink={() => {
            setShowLinkModal(false);
            loadTurmas(); // Reload to show updated links
          }}
          onCancel={() => setShowLinkModal(false)}
        />
      )}

      {/* View Provas Modal */}
      {showProvasModal && selectedTurma && (
        <ViewProvasModal
          turma={selectedTurma}
          onClose={() => setShowProvasModal(false)}
        />
      )}
    </main>
  );
}

// Turma Form Component
interface TurmaFormProps {
  initialData?: TurmaInfo;
  onSubmit: (data: TurmaData) => void;
  onCancel: () => void;
}

function TurmaForm({ initialData, onSubmit, onCancel }: TurmaFormProps) {
  const [formData, setFormData] = useState<TurmaData>({
    ano: initialData?.ano || new Date().getFullYear(),
    materia: initialData?.materia || "",
    curso: initialData?.curso || "",
    periodo: initialData?.periodo || 1,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="form-control">
        <label className="label">
          <span className="label-text">Ano</span>
        </label>
        <input
          type="number"
          className="input input-bordered"
          value={formData.ano}
          onChange={(e) => setFormData({ ...formData, ano: parseInt(e.target.value) })}
          min="2000"
          max="2100"
          required
        />
      </div>

      <div className="form-control">
        <label className="label">
          <span className="label-text">Matéria</span>
        </label>
        <input
          type="text"
          className="input input-bordered"
          value={formData.materia}
          onChange={(e) => setFormData({ ...formData, materia: e.target.value })}
          placeholder="Ex: Matemática"
          required
        />
      </div>

      <div className="form-control">
        <label className="label">
          <span className="label-text">Curso</span>
        </label>
        <input
          type="text"
          className="input input-bordered"
          value={formData.curso}
          onChange={(e) => setFormData({ ...formData, curso: e.target.value })}
          placeholder="Ex: Engenharia"
          required
        />
      </div>

      <div className="form-control">
        <label className="label">
          <span className="label-text">Período</span>
        </label>
        <select
          className="select select-bordered"
          value={formData.periodo}
          onChange={(e) => setFormData({ ...formData, periodo: parseInt(e.target.value) })}
          required
        >
          <option value={1}>1º Período</option>
          <option value={2}>2º Período</option>
          <option value={3}>3º Período</option>
          <option value={4}>4º Período</option>
        </select>
      </div>

      <div className="modal-action">
        <button type="button" className="btn btn-ghost" onClick={onCancel}>
          Cancelar
        </button>
        <button type="submit" className="btn btn-primary">
          {initialData ? 'Atualizar' : 'Criar'}
        </button>
      </div>
    </form>
  );
}

// Link Prova Modal Component
interface LinkProvaModalProps {
  turma: TurmaInfo;
  onLink: () => void;
  onCancel: () => void;
}

function LinkProvaModal({ turma, onLink, onCancel }: LinkProvaModalProps) {
  const [provas, setProvas] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProva, setSelectedProva] = useState<string>("");
  const [linking, setLinking] = useState(false);

  useEffect(() => {
    loadProvas();
  }, []);

  const loadProvas = async () => {
    try {
      setLoading(true);
      const response = await randomizacaoApi.getProvasDisponiveisParaTurma(turma.id);
      setProvas(response.disponiveis);
    } catch (err) {
      console.error('Erro ao carregar provas:', err);
      alert('Erro ao carregar provas disponíveis');
    } finally {
      setLoading(false);
    }
  };

  const handleLink = async () => {
    if (!selectedProva) {
      alert('Selecione uma prova para vincular');
      return;
    }

    try {
      setLinking(true);
      await randomizacaoApi.linkProvaToTurma(turma.id, selectedProva);
      onLink();
    } catch (err: any) {
      console.error('Erro ao vincular prova:', err);
      const errorMessage = err?.response?.data?.detail || 'Erro ao vincular prova à turma';
      alert(errorMessage);
    } finally {
      setLinking(false);
    }
  };

  return (
    <div className="modal modal-open">
      <div className="modal-box max-w-2xl">
        <h3 className="font-bold text-lg mb-4">
          Vincular Prova à Turma: {turma.materia} - {turma.curso}
        </h3>

        {loading ? (
          <div className="flex justify-center py-8">
            <span className="loading loading-spinner loading-lg"></span>
          </div>
        ) : provas.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600">Nenhuma prova disponível para vincular</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="form-control">
              <label className="label">
                <span className="label-text">Selecione uma Prova</span>
              </label>
              <select
                className="select select-bordered"
                value={selectedProva}
                onChange={(e) => setSelectedProva(e.target.value)}
              >
                <option value="">Escolha uma prova...</option>
                {provas.map((prova) => (
                  <option key={prova.id} value={prova.id}>
                    {prova.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        <div className="modal-action">
          <button
            type="button"
            className="btn btn-ghost"
            onClick={onCancel}
            disabled={linking}
          >
            Cancelar
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleLink}
            disabled={linking || !selectedProva}
          >
            {linking && <span className="loading loading-spinner loading-sm"></span>}
            Vincular Prova
          </button>
        </div>
      </div>
    </div>
  );
}

// View Provas Modal Component
interface ViewProvasModalProps {
  turma: TurmaInfo;
  onClose: () => void;
}

function ViewProvasModal({ turma, onClose }: ViewProvasModalProps) {
  const [provas, setProvas] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProvas();
  }, []);

  const loadProvas = async () => {
    try {
      setLoading(true);
      const response = await randomizacaoApi.getProvasDisponiveisParaTurma(turma.id);
      setProvas(response.vinculadas);
    } catch (err) {
      console.error('Erro ao carregar provas vinculadas:', err);
      alert('Erro ao carregar provas vinculadas');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal modal-open">
      <div className="modal-box max-w-4xl">
        <h3 className="font-bold text-lg mb-4">
          Provas Vinculadas: {turma.materia} - {turma.curso}
        </h3>

        {loading ? (
          <div className="flex justify-center py-8">
            <span className="loading loading-spinner loading-lg"></span>
          </div>
        ) : provas.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-600">Nenhuma prova vinculada a esta turma</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table table-zebra">
              <thead>
                <tr>
                  <th>Nome da Prova</th>
                  <th>Data de Vinculação</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {provas.map((prova) => (
                  <tr key={prova.id}>
                    <td>{prova.name}</td>
                    <td>{new Date(prova.created_at).toLocaleDateString('pt-BR')}</td>
                    <td>
                      <button
                        className="btn btn-sm btn-primary btn-outline gap-2"
                        onClick={() => {
                          window.location.href = `/alunos-provas/${turma.id}/${prova.id}`;
                        }}
                      >
                        <Eye className="w-4 h-4" />
                        Ver Alunos
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="modal-action">
          <button
            type="button"
            className="btn btn-primary"
            onClick={onClose}
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
