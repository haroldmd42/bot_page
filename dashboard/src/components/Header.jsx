import React from 'react';
import { Bot, RefreshCw, Radio, Sparkles, Terminal, ShieldCheck } from 'lucide-react';

export default function Header({ lastUpdated, onRefresh, isRefreshing, onOpenTriggerModal }) {
  const formatTime = (isoStr) => {
    if (!isoStr) return 'Reciente';
    try {
      const d = new Date(isoStr);
      return d.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' }) + ' (' + d.toLocaleDateString('es-ES') + ')';
    } catch {
      return isoStr;
    }
  };

  return (
    <header className="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Logo & System Brand */}
          <div className="flex items-center space-x-3.5">
            <div className="relative">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-yellow-400 via-amber-500 to-rose-500 flex items-center justify-center shadow-lg shadow-yellow-500/20">
                <Bot className="w-6 h-6 text-slate-950 stroke-[2.5]" />
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full bg-emerald-500 border-2 border-slate-950 flex items-center justify-center animate-pulse">
                <div className="w-1.5 h-1.5 rounded-full bg-white"></div>
              </div>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-black text-white font-display tracking-tight flex items-center gap-1.5">
                  VIRAL AGENT <span className="text-yellow-400">PRO</span>
                </h1>
                <span className="text-[10px] bg-yellow-400/10 text-yellow-400 font-extrabold uppercase px-2 py-0.5 rounded-md border border-yellow-400/30">
                  Cost $0
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                Generador Autónomo • Meta Reels & YouTube Shorts • Métricas 100% Reales
              </p>
            </div>
          </div>

          {/* Right Status Indicators & Quick Actions */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Status Pill */}
            <div className="hidden sm:flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-slate-300 font-medium">GitHub Actions:</span>
              <span className="text-emerald-400 font-bold">Activo</span>
            </div>

            {/* Manual Run Trigger Button */}
            <button
              onClick={onOpenTriggerModal}
              className="bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-300 hover:to-amber-400 text-slate-950 font-black px-4 py-1.5 rounded-xl text-xs flex items-center gap-1.5 transition-all shadow-lg shadow-yellow-500/20 active:scale-95"
            >
              <span>🚀</span>
              <span>Ejecutar Bot Ahora</span>
            </button>

            {/* Refresh Button */}
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-300 font-semibold px-3 py-1.5 rounded-xl text-xs flex items-center gap-1.5 transition-all disabled:opacity-50"
              title="Refrescar métricas"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-yellow-400' : ''}`} />
              <span className="hidden sm:inline">{isRefreshing ? 'Cargando...' : 'Actualizar'}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
