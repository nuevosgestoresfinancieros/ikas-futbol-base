import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { I18nProvider } from "@/i18n";
import { useState, useEffect } from "react";
import api from "@/api";
import Layout from "@/components/Layout";
import RgpdBanner from "@/components/RgpdBanner";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Players from "@/pages/Players";
import Families from "@/pages/Families";
import Teams from "@/pages/Teams";
import Matches from "@/pages/Matches";
import Callups from "@/pages/Callups";
import Payments from "@/pages/Payments";
import Authorizations from "@/pages/Authorizations";
import Settings from "@/pages/Settings";
import Inscriptions from "@/pages/Inscriptions";
import Trainings from "@/pages/Trainings";
import Stats from "@/pages/Stats";
import Communications from "@/pages/Communications";
import Reports from "@/pages/Reports";
import Equipment from "@/pages/Equipment";
import SplashScreen from "@/components/SplashScreen";

// Rutas protegidas — verifica sesión activa
const ProtectedRoute = ({ children, user }) => {
  const location = useLocation();
  if (user === null) return <Navigate to="/login" state={{ from: location }} replace />;
  if (user === undefined) return null; // cargando
  return children;
};

function App() {
  const [user, setUser] = useState(undefined); // undefined=cargando, null=no auth, string=autenticado

  useEffect(() => {
    api.get("/auth/me")
      .then((r) => setUser(r.data.username))
      .catch(() => setUser(null));
  }, []);

  const handleLogout = async () => {
    await api.post("/auth/logout");
    setUser(null);
  };

  return (
    <I18nProvider>
      <SplashScreen />
      <BrowserRouter>
        <Routes>
          {/* Ruta pública — Login */}
          <Route path="/login" element={
            user && user !== undefined
              ? <Navigate to="/" replace />
              : <Login onLogin={(u) => setUser(u)} />
          } />

          {/* Rutas protegidas */}
          <Route path="/*" element={
            <ProtectedRoute user={user}>
              <Layout onLogout={handleLogout} user={user}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/inscripciones" element={<Inscriptions />} />
                  <Route path="/jugadores" element={<Players />} />
                  <Route path="/familias" element={<Families />} />
                  <Route path="/equipos" element={<Teams />} />
                  <Route path="/entrenamientos" element={<Trainings />} />
                  <Route path="/partidos" element={<Matches />} />
                  <Route path="/convocatorias" element={<Callups />} />
                  <Route path="/estadisticas" element={<Stats />} />
                  <Route path="/pagos" element={<Payments />} />
                  <Route path="/autorizaciones" element={<Authorizations />} />
                  <Route path="/comunicacion" element={<Communications />} />
                  <Route path="/informes" element={<Reports />} />
                  <Route path="/configuracion" element={<Settings />} />
                  <Route path="/equipamiento" element={<Equipment />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          } />
        </Routes>
        <RgpdBanner />
        <Toaster position="top-right" richColors />
      </BrowserRouter>
    </I18nProvider>
  );
}

export default App;
