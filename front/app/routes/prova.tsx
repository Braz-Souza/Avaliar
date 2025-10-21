/**
 * Prova Route
 */

import { ProvaPage, meta } from '../pages/prova/ProvaPage';
import ProtectedRoute from "../components/ProtectedRoute/ProtectedRoute";

export { meta };

export default function Prova() {
  return (
    <ProtectedRoute>
      <ProvaPage />
    </ProtectedRoute>
  );
}
