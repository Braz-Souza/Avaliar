
import { ArrowLeft } from "lucide-react";
import { NavLink } from "react-router";
import type { Route } from "./+types/prova";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Prova" },
    { name: "description", content: "Plataforma web completa para criação, gestão e aplicação de provas educacionais" },
  ];
}

export default function Prova() {
  return (
    <main className="flex items-center justify-center h-screen bg-base-200">
      <NavLink
        className="absolute top-0 left-0 m-4 btn btn-primary gap-4"
        to="/"
      >
        <ArrowLeft />
        Voltar
      </NavLink>
      { /* Sidebar de baixar latex, pdf */}
      { /* Input de latex */}
      { /* Output de latex */}
    </main>
  );
}