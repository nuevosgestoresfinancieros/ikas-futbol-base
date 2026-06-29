import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { I18nProvider } from "@/i18n";
import Layout from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import Players from "@/pages/Players";
import Families from "@/pages/Families";
import Teams from "@/pages/Teams";
import Matches from "@/pages/Matches";
import Callups from "@/pages/Callups";
import Payments from "@/pages/Payments";
import Authorizations from "@/pages/Authorizations";
import Settings from "@/pages/Settings";

function App() {
  return (
    <I18nProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/jugadores" element={<Players />} />
            <Route path="/familias" element={<Families />} />
            <Route path="/equipos" element={<Teams />} />
            <Route path="/partidos" element={<Matches />} />
            <Route path="/convocatorias" element={<Callups />} />
            <Route path="/pagos" element={<Payments />} />
            <Route path="/autorizaciones" element={<Authorizations />} />
            <Route path="/configuracion" element={<Settings />} />
          </Routes>
        </Layout>
        <Toaster position="top-right" richColors />
      </BrowserRouter>
    </I18nProvider>
  );
}

export default App;
