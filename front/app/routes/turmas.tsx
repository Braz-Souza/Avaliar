import type { Route } from "./+types/home";
import { TurmasPage } from "../pages/turmas/TurmasPage";
import ProtectedRoute from "../components/ProtectedRoute/ProtectedRoute";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Gerenciar Turmas - Avaliar" },
    { name: "description", content: "Gerencie turmas do sistema educacional" },
  ];
}

export default function Turmas() {
  return (
    <ProtectedRoute>
      <TurmasPage />
    </ProtectedRoute>
  );
}
