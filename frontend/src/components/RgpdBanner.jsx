import React, { useState } from "react";
import { Shield, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const STORAGE_KEY = "ikastxiki_rgpd_accepted";

const RgpdBanner = () => {
  const [visible, setVisible] = useState(() => !localStorage.getItem(STORAGE_KEY));

  const accept = () => {
    localStorage.setItem(STORAGE_KEY, "1");
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 sm:p-6">
      <div className="max-w-4xl mx-auto rounded-2xl border border-slate-200 bg-white/95 backdrop-blur-xl shadow-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
            <Shield className="h-5 w-5 text-primary" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-slate-800 mb-1">Privacidad y cookies</p>
            <p className="text-xs text-slate-500 leading-relaxed">
              Esta aplicación utiliza únicamente una <strong>cookie de sesión</strong> estrictamente necesaria para
              mantener tu acceso seguro (HttpOnly, duración 8 horas). No utilizamos cookies de seguimiento
              ni compartimos datos con terceros. El tratamiento de datos se realiza conforme al{" "}
              <strong>RGPD (UE) 2016/679</strong> y la <strong>LOPDGDD 3/2018</strong>.
              Los datos gestionados son de uso exclusivo del club.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0 w-full sm:w-auto">
          <Button onClick={accept} className="h-9 px-5 text-sm flex-1 sm:flex-none">
            Entendido
          </Button>
          <button onClick={accept} className="text-slate-400 hover:text-slate-600 p-1">
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default RgpdBanner;
