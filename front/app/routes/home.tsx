import type { Route } from "./+types/home";
import { HomePage } from "../pages/home/HomePage";
import ProtectedRoute from "../components/ProtectedRoute/ProtectedRoute";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Avaliar" },
    { name: "description", content: "Plataforma web completa para criação, gestão e aplicação de provas educacionais" },
  ];
}

export default function Home() {
  return (
    <ProtectedRoute>
      <HomePage />
    </ProtectedRoute>
  );
}
