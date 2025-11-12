import type { Route } from "./+types/home";
import { AlunosPage } from "../pages/alunos/AlunosPage";
import ProtectedRoute from "../components/ProtectedRoute/ProtectedRoute";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Gerenciar Alunos - Avaliar" },
    { name: "description", content: "Gerencie alunos do sistema educacional" },
  ];
}

export default function Alunos() {
  return (
    <ProtectedRoute>
      <AlunosPage />
    </ProtectedRoute>
  );
}
