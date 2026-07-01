import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock, User, Eye, EyeOff } from "lucide-react";
import { toast } from "sonner";
import api from "@/api";
import { useI18n } from "@/i18n";
import { Button } from "@/components/ui/button";

const Login = ({ onLogin }) => {
  const { t, lang, setLang } = useI18n();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!form.username || !form.password) { toast.error("Introduce usuario y contraseña"); return; }
    setLoading(true);
    try {
      const res = await api.post("/auth/login", form);
      if (onLogin) onLogin(res.data.username);
      navigate("/", { replace: true });
    } catch (err) {
      toast.error(err.response?.data?.detail || "Usuario o contraseña incorrectos");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 via-white to-emerald-50 px-4">
      <div className="w-full max-w-md">
        {/* Logo / Cabecera */}
        <div className="text-center mb-8">
          <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-emerald-400 shadow-lg mb-4">
            <span className="text-3xl">⚽</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 font-heading">Ikas-Txiki Manager</h1>
          <p className="text-slate-500 text-sm mt-1">
            {lang === "eu" ? "Sartu zure kontura" : "Accede a tu cuenta"}
          </p>
        </div>

        {/* Selector de idioma */}
        <div className="flex justify-center gap-2 mb-6">
          {["es", "eu"].map((l) => (
            <button key={l} onClick={() => setLang(l)}
              className={`px-3 py-1 rounded-full text-xs font-semibold transition-all
                ${lang === l ? "bg-primary text-white" : "bg-slate-100 text-slate-500 hover:bg-slate-200"}`}>
              {l === "es" ? "Castellano" : "Euskera"}
            </button>
          ))}
        </div>

        {/* Formulario */}
        <form onSubmit={submit} className="rounded-2xl border border-white/60 bg-white/80 backdrop-blur-xl shadow-xl p-8 space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              {lang === "eu" ? "Erabiltzailea" : "Usuario"}
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={form.username}
                onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
                placeholder={lang === "eu" ? "Erabiltzaile izena" : "Nombre de usuario"}
                autoComplete="username"
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              {lang === "eu" ? "Pasahitza" : "Contraseña"}
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type={showPwd ? "text" : "password"}
                value={form.password}
                onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                placeholder="••••••••"
                autoComplete="current-password"
                className="w-full pl-10 pr-10 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
              <button type="button" onClick={() => setShowPwd(!showPwd)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                {showPwd ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          <Button type="submit" disabled={loading} className="w-full h-11 text-base font-semibold">
            {loading
              ? (lang === "eu" ? "Sartzen..." : "Accediendo...")
              : (lang === "eu" ? "Sartu" : "Acceder")}
          </Button>
        </form>

        {/* Pie */}
        <p className="text-center text-xs text-slate-400 mt-6">
          © {new Date().getFullYear()} Ikas-Txiki Manager · 
          <a href="https://docencia.cibermedida.es" target="_blank" rel="noreferrer" className="hover:text-primary ml-1">
            Cibermedida
          </a>
        </p>
      </div>
    </div>
  );
};

export default Login;
