/**
 * Alunos Management Page
 * CRUD operations for alunos with turma management
 */

import { useState, useEffect } from "react";
import { Link } from "react-router";
import { alunosApi, turmasApi, type AlunoInfo, type AlunoData, type TurmaInfo } from "../../services/api";
import { UserPlus, Edit, Trash2, Search, Users, GraduationCap, Plus, Minus } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";

export function AlunosPage() {
  const { user } = useAuth();
  const [alunos, setAlunos] = useState<AlunoInfo[]>([]);
  const [turmas, setTurmas] = useState<TurmaInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterTurma, setFilterTurma] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingAluno, setEditingAluno] = useState<AlunoInfo | null>(null);
  const [managingTurmas, setManagingTurmas] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [alunosData, turmasData] = await Promise.all([
        alunosApi.list(),
        turmasApi.list()
      ]);
      setAlunos(alunosData);
      setTurmas(turmasData);
      setError(null);
    } catch (err) {
      console.error('Erro ao carregar dados:', err);
      setError('Erro ao carregar os dados');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (alunoId: string, alunoName: string) => {
    if (!confirm(`Tem certeza que deseja excluir o aluno "${alunoName}"?`)) {
      return;
    }

    try {
      setDeletingId(alunoId);
      await alunosApi.delete(alunoId);
      setAlunos(alunos.filter(a => a.id !== alunoId));
    } catch (err) {
      console.error('Erro ao excluir aluno:', err);
      alert('Erro ao excluir o aluno');
    } finally {
      setDeletingId(null);
    }
  };

  const handleCreate = async (formData: AlunoData) => {
    try {
      const newAluno = await alunosApi.create(formData);
      setAlunos([...alunos, newAluno]);
      setShowCreateModal(false);
    } catch (err) {
      console.error('Erro ao criar aluno:', err);
      alert('Erro ao criar o aluno');
    }
  };

  const handleUpdate = async (alunoId: string, formData: Partial<AlunoData>) => {
    try {
      const updatedAluno = await alunosApi.update(alunoId, formData);
      setAlunos(alunos.map(a => a.id === alunoId ? updatedAluno : a));
      setEditingAluno(null);
    } catch (err) {
      console.error('Erro ao atualizar aluno:', err);
      alert('Erro ao atualizar o aluno');
    }
  };

  const handleAddToTurma = async (alunoId: string, turmaId: string) => {
    try {
      const updatedAluno = await alunosApi.addToTurma(alunoId, turmaId);
      setAlunos(alunos.map(a => a.id === alunoId ? updatedAluno : a));
    } catch (err) {
      console.error('Erro ao adicionar aluno à turma:', err);
      alert('Erro ao adicionar aluno à turma');
    }
  };

  const handleRemoveFromTurma = async (alunoId: string, turmaId: string) => {
    try {
      const updatedAluno = await alunosApi.removeFromTurma(alunoId, turmaId);
      setAlunos(alunos.map(a => a.id === alunoId ? updatedAluno : a));
    } catch (err) {
      console.error('Erro ao remover aluno da turma:', err);
      alert('Erro ao remover aluno da turma');
    }
  };

  const filteredAlunos = alunos.filter(aluno => {
    const matchesSearch = aluno.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         aluno.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         aluno.matricula.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTurma = !filterTurma || aluno.turmas.some(t => t.id === filterTurma);
    return matchesSearch && matchesTurma;
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
              <h1 className="text-xl font-semibold">Gerenciar Alunos</h1>
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
        <div className="w-full max-w-7xl mx-auto">
          <div className="card bg-base-100 shadow-xl p-6">
            {/* Header with actions and filters */}
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-6 space-y-4 lg:space-y-0">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="btn btn-primary gap-2"
                >
                  <UserPlus className="w-5 h-5" />
                  Novo Aluno
                </button>
              </div>

              <div className="flex flex-col sm:flex-row gap-2">
                <div className="form-control">
                  <div className="input-group">
                    <Search className="w-4 h-4" />
                    <input
                      type="text"
                      placeholder="Buscar alunos..."
                      className="input input-bordered"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>

                <select
                  className="select select-bordered"
                  value={filterTurma}
                  onChange={(e) => setFilterTurma(e.target.value)}
                >
                  <option value="">Todas as turmas</option>
                  {turmas.map(turma => (
                    <option key={turma.id} value={turma.id}>
                      {turma.materia} - {turma.curso} ({turma.ano})
                    </option>
                  ))}
                </select>
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
            ) : filteredAlunos.length === 0 ? (
              <div className="text-center py-12">
                <Users className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600 mb-4">
                  {searchTerm || filterTurma
                    ? 'Nenhum aluno encontrado com os filtros aplicados'
                    : 'Nenhum aluno cadastrado ainda'}
                </p>
                {!searchTerm && !filterTurma && (
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="btn btn-primary btn-sm"
                  >
                    Criar primeiro aluno
                  </button>
                )}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="table table-zebra">
                  <thead>
                    <tr>
                      <th>Nome</th>
                      <th>Email</th>
                      <th>Matrícula</th>
                      <th>Turmas</th>
                      <th className="text-right">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredAlunos.map((aluno) => (
                      <tr key={aluno.id}>
                        <td className="font-medium">{aluno.nome}</td>
                        <td>{aluno.email}</td>
                        <td>{aluno.matricula}</td>
                        <td>
                          <div className="flex flex-wrap gap-1">
                            {aluno.turmas.map(turma => (
                              <span
                                key={turma.id}
                                className="badge badge-primary badge-sm"
                              >
                                {turma.materia}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td>
                          <div className="flex gap-2 justify-end">
                            <button
                              onClick={() => setEditingAluno(aluno)}
                              className="btn btn-sm btn-primary btn-outline gap-2"
                            >
                              <Edit className="w-4 h-4" />
                              Editar
                            </button>
                            <button
                              onClick={() => setManagingTurmas(aluno.id)}
                              className="btn btn-sm btn-secondary btn-outline gap-2"
                            >
                              <GraduationCap className="w-4 h-4" />
                              Turmas
                            </button>
                            <button
                              className={`btn btn-sm btn-error btn-outline gap-2 ${
                                deletingId === aluno.id ? 'loading' : ''
                              }`}
                              onClick={() => handleDelete(aluno.id, aluno.nome)}
                              disabled={deletingId === aluno.id}
                            >
                              {deletingId !== aluno.id && (
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
            <h3 className="font-bold text-lg mb-4">Novo Aluno</h3>
            <AlunoForm
              turmas={turmas}
              onSubmit={handleCreate}
              onCancel={() => setShowCreateModal(false)}
            />
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editingAluno && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">Editar Aluno</h3>
            <AlunoForm
              initialData={editingAluno}
              turmas={turmas}
              onSubmit={(data) => handleUpdate(editingAluno.id, data)}
              onCancel={() => setEditingAluno(null)}
            />
          </div>
        </div>
      )}

      {/* Manage Turmas Modal */}
      {managingTurmas && (
        <div className="modal modal-open">
          <div className="modal-box w-11/12 max-w-4xl">
            <h3 className="font-bold text-lg mb-4">
              Gerenciar Turmas - {alunos.find(a => a.id === managingTurmas)?.nome}
            </h3>
            <TurmaManager
              aluno={alunos.find(a => a.id === managingTurmas)!}
              turmas={turmas}
              onAddToTurma={handleAddToTurma}
              onRemoveFromTurma={handleRemoveFromTurma}
              onClose={() => setManagingTurmas(null)}
            />
          </div>
        </div>
      )}
    </main>
  );
}

// Aluno Form Component
interface AlunoFormProps {
  initialData?: AlunoInfo;
  turmas: TurmaInfo[];
  onSubmit: (data: AlunoData) => void;
  onCancel: () => void;
}

function AlunoForm({ initialData, turmas, onSubmit, onCancel }: AlunoFormProps) {
  const [formData, setFormData] = useState<AlunoData>({
    nome: initialData?.nome || "",
    email: initialData?.email || "",
    matricula: initialData?.matricula || "",
    turma_ids: initialData?.turmas.map(t => t.id) || [],
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleTurmaChange = (turmaId: string, checked: boolean) => {
    if (checked) {
      setFormData({ ...formData, turma_ids: [...formData.turma_ids, turmaId] });
    } else {
      setFormData({ ...formData, turma_ids: formData.turma_ids.filter(id => id !== turmaId) });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="form-control">
        <label className="label">
          <span className="label-text">Nome</span>
        </label>
        <input
          type="text"
          className="input input-bordered"
          value={formData.nome}
          onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
          placeholder="Nome completo do aluno"
          required
        />
      </div>

      <div className="form-control">
        <label className="label">
          <span className="label-text">Email</span>
        </label>
        <input
          type="email"
          className="input input-bordered"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          placeholder="email@exemplo.com"
          required
        />
      </div>

      <div className="form-control">
        <label className="label">
          <span className="label-text">Matrícula</span>
        </label>
        <input
          type="text"
          className="input input-bordered"
          value={formData.matricula}
          onChange={(e) => setFormData({ ...formData, matricula: e.target.value })}
          placeholder="2024001234"
          required
        />
      </div>

      <div className="form-control">
        <label className="label">
          <span className="label-text">Turmas (selecione pelo menos uma)</span>
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-40 overflow-y-auto border rounded p-2">
          {turmas.map(turma => (
            <label key={turma.id} className="flex items-center space-x-2 cursor-pointer hover:bg-base-200 p-1 rounded">
              <input
                type="checkbox"
                className="checkbox"
                checked={formData.turma_ids.includes(turma.id)}
                onChange={(e) => handleTurmaChange(turma.id, e.target.checked)}
              />
              <span className="text-sm">
                {turma.materia} - {turma.curso} ({turma.ano} - {turma.periodo}º)
              </span>
            </label>
          ))}
        </div>
      </div>

      <div className="modal-action">
        <button type="button" className="btn btn-ghost" onClick={onCancel}>
          Cancelar
        </button>
        <button
          type="submit"
          className="btn btn-primary"
          disabled={formData.turma_ids.length === 0}
        >
          {initialData ? 'Atualizar' : 'Criar'}
        </button>
      </div>
    </form>
  );
}

// Turma Manager Component
interface TurmaManagerProps {
  aluno: AlunoInfo;
  turmas: TurmaInfo[];
  onAddToTurma: (alunoId: string, turmaId: string) => void;
  onRemoveFromTurma: (alunoId: string, turmaId: string) => void;
  onClose: () => void;
}

function TurmaManager({ aluno, turmas, onAddToTurma, onRemoveFromTurma, onClose }: TurmaManagerProps) {
  const [loading, setLoading] = useState<string | null>(null);

  const handleAdd = async (turmaId: string) => {
    setLoading(turmaId);
    await onAddToTurma(aluno.id, turmaId);
    setLoading(null);
  };

  const handleRemove = async (turmaId: string) => {
    setLoading(turmaId);
    await onRemoveFromTurma(aluno.id, turmaId);
    setLoading(null);
  };

  const availableTurmas = turmas.filter(t => !aluno.turmas.some(at => at.id === t.id));

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Current Turmas */}
        <div>
          <h4 className="font-semibold mb-2">Turmas Atuais</h4>
          <div className="space-y-2">
            {aluno.turmas.length === 0 ? (
              <p className="text-gray-500 text-sm">Este aluno não está em nenhuma turma</p>
            ) : (
              aluno.turmas.map(turma => (
                <div key={turma.id} className="flex items-center justify-between p-2 bg-base-200 rounded">
                  <span className="text-sm">
                    {turma.materia} - {turma.curso} ({turma.ano})
                  </span>
                  <button
                    onClick={() => handleRemove(turma.id)}
                    className={`btn btn-xs btn-error btn-outline gap-1 ${
                      loading === turma.id ? 'loading' : ''
                    }`}
                    disabled={loading === turma.id || aluno.turmas.length === 1}
                  >
                    {loading !== turma.id && <Minus className="w-3 h-3" />}
                    Remover
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Available Turmas */}
        <div>
          <h4 className="font-semibold mb-2">Turmas Disponíveis</h4>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {availableTurmas.length === 0 ? (
              <p className="text-gray-500 text-sm">Este aluno já está em todas as turmas</p>
            ) : (
              availableTurmas.map(turma => (
                <div key={turma.id} className="flex items-center justify-between p-2 bg-base-200 rounded">
                  <span className="text-sm">
                    {turma.materia} - {turma.curso} ({turma.ano})
                  </span>
                  <button
                    onClick={() => handleAdd(turma.id)}
                    className={`btn btn-xs btn-primary btn-outline gap-1 ${
                      loading === turma.id ? 'loading' : ''
                    }`}
                    disabled={loading === turma.id}
                  >
                    {loading !== turma.id && <Plus className="w-3 h-3" />}
                    Adicionar
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="modal-action">
        <button className="btn btn-primary" onClick={onClose}>
          Fechar
        </button>
      </div>
    </div>
  );
}
