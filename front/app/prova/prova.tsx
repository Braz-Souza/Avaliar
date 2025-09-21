
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
      <div className="flex flex-col max-w-36">
        <NavLink
          className="btn btn-primary gap-4 flex-1 p-2 m-2"
          to="/"
        >
          <ArrowLeft />
          Voltar
        </NavLink>
        <button
          className="btn btn-primary btn-outline flex-1 p-2 m-2"
          >
          Baixar PDF
        </button>
        <button
          className="btn btn-primary btn-outline flex-1 p-2 m-2"
          >
          Baixar Latex
        </button>
      </div>
      <div className="h-full w-fit bg-base-400 flex flex-1 p-8 gap-8">
        <textarea className="bg-base-100 shadow textarea flex flex-1 h-full" placeholder="Insert LaTeX here"></textarea>
        <div className="bg-base-100 shadow textarea flex flex-1 h-full w-full">
          <object data="./sample.pdf" type="application/pdf" className="w-full">
              <div>No PDF available</div>
          </object>
        </div>
      </div>
    </main>
  );
}