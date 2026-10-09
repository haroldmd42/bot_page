import React from 'react';
import { DollarSign, Award, Lightbulb, Zap, ArrowUpRight, CheckCircle2 } from 'lucide-react';

export default function MonetizationTips({
  overview = {},
  recommendations = []
}) {
  const ytMonetization = overview.youtube_shorts_monetization || {
    target_views: 10000000,
    current_views: 297000,
    percentage: 2.97,
    estimated_earnings_usd: 23.76
  };

  const fbMonetization = overview.facebook_reels_monetization || {
    target_views: 500000,
    current_views: 347400,
    percentage: 69.48,
    estimated_earnings_usd: 52.11
  };

  const formatNumber = (num) => (num ? num.toLocaleString() : '0');

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Monetization Goals Card */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-white font-display flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-emerald-400" />
              Progreso hacia Monetización ($0 Infra)
            </h3>
            <span className="text-xs bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-full border border-emerald-500/30 font-semibold flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> En Carrera
            </span>
          </div>

          <p className="text-xs text-slate-400 mb-6">
            Monitoreo continuo hacia el Programa de Socios de YouTube (10M vistas en Shorts) y los Bonos de Desempeño de Meta Reels.
          </p>

          <div className="space-y-6">
            {/* Meta Reels Progress */}
            <div>
              <div className="flex justify-between items-center text-xs mb-1.5 font-semibold">
                <span className="text-blue-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                  Meta Reels (Bono de Desempeño 500k)
                </span>
                <span className="text-white">
                  {formatNumber(fbMonetization.current_views)} / {formatNumber(fbMonetization.target_views)} ({fbMonetization.percentage}%)
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden border border-slate-700/60 p-0.5">
                <div
                  className="bg-gradient-to-r from-blue-500 to-indigo-500 h-full rounded-full transition-all duration-1000 shadow-sm"
                  style={{ width: `${Math.min(fbMonetization.percentage, 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-[11px] text-slate-500 mt-1">
                <span>Ingreso estimado: ~${fbMonetization.estimated_earnings_usd} USD</span>
                <span className="text-blue-400 font-medium">Meta Milestone cercano 🔥</span>
              </div>
            </div>

            {/* YouTube Shorts Progress */}
            <div>
              <div className="flex justify-between items-center text-xs mb-1.5 font-semibold">
                <span className="text-rose-400 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                  YouTube Shorts (Partner Program 10M)
                </span>
                <span className="text-white">
                  {formatNumber(ytMonetization.current_views)} / 10,000,000 ({ytMonetization.percentage}%)
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-3 overflow-hidden border border-slate-700/60 p-0.5">
                <div
                  className="bg-gradient-to-r from-rose-500 to-yellow-500 h-full rounded-full transition-all duration-1000"
                  style={{ width: `${Math.max(ytMonetization.percentage, 2)}%` }}
                />
              </div>
              <div className="flex justify-between text-[11px] text-slate-500 mt-1">
                <span>Ingreso estimado Shorts: ~${ytMonetization.estimated_earnings_usd} USD</span>
                <span className="text-slate-400">90 días de periodo rotativo</span>
              </div>
            </div>
          </div>
        </div>

        {/* Top Performer Ribbon */}
        {overview.top_performing_hook && (
          <div className="mt-6 pt-5 border-t border-slate-800/80 bg-slate-900/40 -mx-6 -mb-6 p-6 rounded-b-2xl">
            <div className="flex items-start gap-3">
              <Award className="w-5 h-5 text-yellow-400 shrink-0 mt-0.5" />
              <div>
                <span className="text-[11px] uppercase font-bold tracking-wider text-yellow-400">
                  Gancho Más Viral Detectado (Feedback Loop)
                </span>
                <p className="text-xs text-slate-200 font-medium mt-1 italic">
                  "{overview.top_performing_hook}"
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Growth Optimizer AI Recommendations Card */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-white font-display flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              Recomendaciones del Optimizador Autónomo
            </h3>
            <span className="text-xs bg-yellow-400/10 text-yellow-400 px-2.5 py-1 rounded-full border border-yellow-400/30 font-semibold">
              Feedback Loop Activo
            </span>
          </div>

          <p className="text-xs text-slate-400 mb-4">
            El motor analiza los picos de retención e interacción de tus publicaciones y reajusta automáticamente las siguientes generaciones.
          </p>

          <div className="space-y-3.5">
            {recommendations && recommendations.length > 0 ? (
              recommendations.map((tip, idx) => (
                <div
                  key={idx}
                  className="bg-slate-900/60 border border-slate-800 hover:border-slate-700/80 rounded-xl p-3.5 transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                      <Lightbulb className="w-3.5 h-3.5 text-yellow-400" />
                      {tip.title}
                    </span>
                    <span
                      className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded ${
                        tip.priority === 'HIGH'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                      }`}
                    >
                      {tip.priority}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed pl-5">
                    {tip.description}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500">Recopilando datos para las primeras recomendaciones...</p>
            )}
          </div>
        </div>

        <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
          <span>Próxima ejecución programada:</span>
          <span className="font-mono text-yellow-400 font-semibold">14:00 UTC (Diario)</span>
        </div>
      </div>
    </div>
  );
}
