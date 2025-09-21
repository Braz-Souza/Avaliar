import logoDark from "./logo-dark.svg";
import logoLight from "./logo-light.svg";
import { Link } from "react-router";

export function Start() {
  return (
    <main className="flex items-center justify-center h-screen bg-base-200">
      <header className="absolute top-12 w-[500px] max-w-[100vw] p-4">
        <img
          src={logoLight}
          alt="Avaliar Logo"
          className="block w-full dark:hidden"
        />
        <img
          src={logoDark}
          alt="Avaliar Logo"
          className="hidden w-full dark:block"
        />
      </header>
      <div className="card bg-base-100 shadow p-12 py-24">
        <Link
          className="btn btn-primary"
          to="/prova"
          >
          Gerar Prova
        </Link>
      </div>
    </main>
  );
}