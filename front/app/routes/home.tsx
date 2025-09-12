import type { Route } from "./+types/home";
import { Welcome } from "../welcome/welcome";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Avaliar" },
    { name: "description", content: "Pagina inicial" },
  ];
}

export default function Home() {
  return <Welcome />;
}
