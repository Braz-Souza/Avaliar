import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("prova","prova/prova.tsx")
] satisfies RouteConfig;
