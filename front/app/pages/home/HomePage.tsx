/**
 * Home Page
 * Lista de provas salvas
 */

import logoDark from "./assets/logo-dark.svg";
import logoLight from "./assets/logo-light.svg";
import { Link } from "react-router";
import { useState, useEffect } from "react";
import { provasApi, type ProvaInfo } from "../../services/api";
import { FileText, Trash2, Edit, PlusCircle, LogOut, User, GraduationCap, Users } from "lucide-react";
import { formatDate } from "../../utils/date-formatter";
import { useAuth } from "../../contexts/AuthContext";

export function HomePage() {
  const { user, logout } = useAuth();
  const [provas, setProvas] = useState<ProvaInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    loadProvas();
  }, []);

  const loadProvas = async () => {
    try {
      setLoading(true);
      const data = await provasApi.list();
      setProvas(data);
      setError(null);
    } catch (err) {
      console.error('Erro ao carregar provas:', err);
      setError('Erro ao carregar as provas');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (provaId: string, provaName: string) => {
    if (!confirm(`Tem certeza que deseja excluir a prova "${provaName}"?`)) {
      return;
    }

    try {
      setDeletingId(provaId);
      await provasApi.delete(provaId);
      setProvas(provas.filter(p => p.id !== provaId));
    } catch (err) {
      console.error('Erro ao excluir prova:', err);
      alert('Erro ao excluir a prova');
    } finally {
      setDeletingId(null);
    }
  };

  const handleLogout = () => {
    if (confirm('Tem certeza que deseja sair?')) {
      logout();
    }
  };

  return (
    <main className="flex flex-col min-h-screen bg-base-200">
      <header className="w-full bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <img
                src={logoLight}
                alt="Avaliar Logo"
                className="h-8 w-auto dark:hidden"
              />
              <img
                src={logoDark}
                alt="Avaliar Logo"
                className="h-8 w-auto hidden dark:block"
              />
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-gray-700">
                <User className="w-4 h-4" />
                <span className="text-sm font-medium">
                  {user?.name || 'Usuário'}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Sair</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-4xl">
        <div className="card bg-base-100 shadow-xl p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Minhas Provas</h2>
            <div className="flex gap-2">
              <Link className="btn btn-primary gap-2" to="/prova">
                <PlusCircle className="w-5 h-5" />
                Nova Prova
              </Link>
              <Link className="btn btn-secondary gap-2" to="/turmas">
                <GraduationCap className="w-5 h-5" />
                Gerenciar Turmas
              </Link>
              <Link className="btn btn-accent gap-2" to="/alunos">
                <Users className="w-5 h-5" />
                Gerenciar Alunos
              </Link>
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
          ) : provas.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-600 mb-4">Nenhuma prova salva ainda</p>
              <Link className="btn btn-primary btn-sm" to="/prova">
                Criar minha primeira prova
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="table table-zebra">
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Criada em</th>
                    <th>Modificada em</th>
                    <th className="text-right">Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {provas.map((prova) => (
                    <tr key={prova.id}>
                      <td className="font-medium">{prova.name}</td>
                      <td className="text-sm text-gray-600">
                        {formatDate(prova.created_at)}
                      </td>
                      <td className="text-sm text-gray-600">
                        {formatDate(prova.modified_at)}
                      </td>
                      <td>
                        <div className="flex gap-2 justify-end">
                          <Link
                            to={`/prova?id=${prova.id}`}
                            className="btn btn-sm btn-primary btn-outline gap-2"
                          >
                            <Edit className="w-4 h-4" />
                            Editar
                          </Link>
                          <button
                            className={`btn btn-sm btn-error btn-outline gap-2 ${
                              deletingId === prova.id ? 'loading' : ''
                            }`}
                            onClick={() => handleDelete(prova.id, prova.name)}
                            disabled={deletingId === prova.id}
                          >
                            {deletingId !== prova.id && (
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
    </main>
  );
}
