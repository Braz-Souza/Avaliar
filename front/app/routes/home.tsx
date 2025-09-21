import type { Route } from "./+types/home";
import { Start } from "../start/start";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Avaliar" },
    { name: "description", content: "Plataforma web completa para criação, gestão e aplicação de provas educacionais" },
  ];
}

export default function Home() {
  return <Start />;
}
