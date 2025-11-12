import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("login", "routes/login.tsx"),
  route("prova", "routes/prova.tsx"),
  route("turmas", "routes/turmas.tsx"),
  route("alunos", "routes/alunos.tsx")
] satisfies RouteConfig;
