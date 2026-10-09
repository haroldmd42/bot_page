import React, { useState, useEffect } from 'react';
import {
  Eye,
  Heart,
  TrendingUp,
  Video,
  DollarSign,
  Share2,
  Calendar,
  AlertCircle,
  HelpCircle,
  Terminal,
  Layers,
  Sparkles
} from 'lucide-react';

import Header from './components/Header';
import MetricCard from './components/MetricCard';
import GrowthChart from './components/GrowthChart';
import MonetizationTips from './components/MonetizationTips';
import VideoTable from './components/VideoTable';

// Default static fallback data in case of direct local file protocol
const fallbackHistory = [
  {
    "id": "vid_20261001_01",
    "title": "3 Webs con IA que parecen ILEGALES de conocer en 2026 🤖",
    "hook": "¿Sigues usando ChatGPT como en 2023? Estas 3 webs te vuelan la cabeza.",
    "niche": "Tech & AI",
    "created_at": "2026-10-01T14:00:00Z",
    "duration": 38.5,
    "status": "published",
    "youtube": { "video_id": "yt_sample_01", "url": "https://youtube.com/shorts/yt_sample_01", "views": 48200, "likes": 3950, "comments": 312 },
    "facebook": { "video_id": "fb_sample_01", "url": "https://facebook.com/reel/fb_sample_01", "views": 62400, "likes": 5120, "comments": 488, "shares": 1240 },
    "metrics_summary": { "total_views": 110600, "total_likes": 9070, "total_comments": 800, "total_shares": 1240, "engagement_rate": 9.87 }
  },
  {
    "id": "vid_20261004_04",
    "title": "Por qué NO Deberías Aprender a Programar en 2026 (La Verdad) 💻",
    "hook": "No aprendas sintaxis básica. Si no sabes orquestar agentes IA, estás fuera.",
    "niche": "Tech & AI",
    "created_at": "2026-10-04T14:00:00Z",
    "duration": 40.0,
    "status": "published",
    "youtube": { "video_id": "yt_sample_04", "url": "https://youtube.com/shorts/yt_sample_04", "views": 98400, "likes": 9150, "comments": 1140 },
    "facebook": { "video_id": "fb_sample_04", "url": "https://facebook.com/reel/fb_sample_04", "views": 115200, "likes": 10450, "comments": 1580, "shares": 3410 },
    "metrics_summary": { "total_views": 213600, "total_likes": 19600, "total_comments": 2720, "total_shares": 3410, "engagement_rate": 12.04 }
  }
];

const fallbackMetrics = {
  "last_updated": new Date().toISOString(),
  "overview": {
    "total_videos": 5,
    "total_views": 644400,
    "total_likes": 55800,
    "total_comments": 5896,
    "total_shares": 8100,
    "average_engagement_rate": 10.83,
    "top_performing_niche": "Tech & AI",
    "top_performing_hook": "No aprendas sintaxis básica. Si no sabes orquestar agentes IA, estás fuera.",
    "youtube_shorts_monetization": {
      "target_views": 10000000,
      "current_views": 297000,
      "percentage": 2.97,
      "estimated_cpm_usd": 0.08,
      "estimated_earnings_usd": 23.76
    },
    "facebook_reels_monetization": {
      "target_views": 500000,
      "current_views": 347400,
      "percentage": 69.48,
      "estimated_cpm_usd": 0.15,
      "estimated_earnings_usd": 52.11
    }
  },
  "growth_trends": [
    { "date": "2026-10-01", "views": 110600, "likes": 9070, "comments": 800, "shares": 1240, "cumulative_views": 110600 },
    { "date": "2026-10-02", "views": 59300, "likes": 4400, "comments": 326, "shares": 380, "cumulative_views": 169900 },
    { "date": "2026-10-03", "views": 163600, "likes": 14720, "comments": 1420, "shares": 2150, "cumulative_views": 333500 },
    { "date": "2026-10-04", "views": 213600, "likes": 19600, "comments": 2720, "shares": 3410, "cumulative_views": 547100 },
    { "date": "2026-10-05", "views": 97300, "likes": 8010, "comments": 630, "shares": 920, "cumulative_views": 644400 }
  ],
  "platform_breakdown": {
    "youtube": { "views": 297000, "share_pct": 46.1 },
    "facebook": { "views": 347400, "share_pct": 53.9 }
  },
  "optimization_recommendations": [
    {
      "type": "hook_strategy",
      "priority": "HIGH",
      "title": "Ganchos de Confrontación Directa (+38% Retención)",
      "description": "Los ganchos que desafían una creencia popular superaron la media en un +65% de reproducciones totales."
    },
    {
      "type": "pacing",
      "priority": "MEDIUM",
      "title": "Cortes visuales cada 2.8 segundos",
      "description": "La tasa de finalización creció un 22% cuando se insertan cambios de escena cada 3 segundos."
    }
  ]
};

export default function App() {
  const [history, setHistory] = useState(fallbackHistory);
  const [metrics, setMetrics] = useState(fallbackMetrics);
  const [loading, setLoading] = useState(false);
  const [showCliGuide, setShowCliGuide] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      // Try to load dynamic data from public/data/ or root data/
      const [historyRes, metricsRes] = await Promise.allSettled([
        fetch('./data/history.json').then((r) => (r.ok ? r.json() : Promise.reject(r))),
        fetch('./data/metrics.json').then((r) => (r.ok ? r.json() : Promise.reject(r)))
      ]);

      if (historyRes.status === 'fulfilled') {
        setHistory(historyRes.value);
      }
      if (metricsRes.status === 'fulfilled') {
        setMetrics(metricsRes.value);
      }
    } catch (err) {
      console.warn('Using bundled fallback analytics data.', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const overview = metrics.overview || {};
  const totalEarnings = (
    (overview.youtube_shorts_monetization?.estimated_earnings_usd || 0) +
    (overview.facebook_reels_monetization?.estimated_earnings_usd || 0)
  ).toFixed(2);

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col">
      <Header
        lastUpdated={metrics.last_updated}
        onRefresh={loadData}
        isRefreshing={loading}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 flex-1 w-full">
        {/* Banner: Autonomous status */}
        <div className="bg-gradient-to-r from-amber-500/10 via-yellow-500/10 to-indigo-500/10 border border-yellow-500/30 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-3.5">
            <div className="p-2.5 rounded-xl bg-yellow-400/20 text-yellow-400 border border-yellow-400/30">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white font-display">
                Pipeline Autónomo de Contenido $0 Operativo
              </h2>
              <p className="text-xs text-slate-400">
                GitHub Actions ejecuta la creación diaria (14:00 UTC) y actualiza analíticas cada 12 horas.
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowCliGuide(!showCliGuide)}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-yellow-400 hover:text-yellow-300 bg-slate-900/90 border border-yellow-500/30 px-3.5 py-2 rounded-xl transition-all self-start sm:self-auto"
          >
            <Terminal className="w-3.5 h-3.5" />
            {showCliGuide ? 'Ocultar Comandos' : 'Comandos de Ejecución'}
          </button>
        </div>

        {/* Collapsible Execution Guide */}
        {showCliGuide && (
          <div className="glass-panel rounded-2xl p-5 border border-slate-700 space-y-3 text-xs">
            <h4 className="font-bold text-white flex items-center gap-2">
              <Terminal className="w-4 h-4 text-yellow-400" />
              Comandos de Ejecución Manual y Local
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                <span className="text-slate-400 text-[11px] font-semibold block mb-1">
                  1. Publicación Inmediata (Dry Run)
                </span>
                <code className="text-yellow-400 font-mono text-[11px]">
                  python bot/main.py --mode publish --dry-run
                </code>
              </div>
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                <span className="text-slate-400 text-[11px] font-semibold block mb-1">
                  2. Sincronizar Métricas de APIs
                </span>
                <code className="text-blue-400 font-mono text-[11px]">
                  python bot/main.py --mode analytics
                </code>
              </div>
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                <span className="text-slate-400 text-[11px] font-semibold block mb-1">
                  3. Iniciar Dashboard en Desarrollo
                </span>
                <code className="text-emerald-400 font-mono text-[11px]">
                  npm run dev
                </code>
              </div>
            </div>
          </div>
        )}

        {/* Key KPI Metric Cards Grid */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <MetricCard
            title="Reproducciones Totales"
            value={overview.total_views ? overview.total_views.toLocaleString() : '644,400'}
            subValue="Meta + YouTube"
            icon={Eye}
            trend="+24.8%"
            trendDirection="up"
            colorScheme="yellow"
          />
          <MetricCard
            title="Tasa de Engagement"
            value={`${overview.average_engagement_rate || 10.8}%`}
            subValue="Likes + Comentarios + Shares"
            icon={TrendingUp}
            trend="+1.9%"
            trendDirection="up"
            colorScheme="emerald"
          />
          <MetricCard
            title="Videos Publicados"
            value={overview.total_videos || history.length}
            subValue="100% Automatizados"
            icon={Video}
            trend="+1 Hoy"
            trendDirection="up"
            colorScheme="blue"
          />
          <MetricCard
            title="Ganancia Estimada"
            value={`$${totalEarnings} USD`}
            subValue="Shorts AdRev + Reels Bonus"
            icon={DollarSign}
            trend="+32.4%"
            trendDirection="up"
            colorScheme="purple"
          />
        </section>

        {/* Charts & Visual Analytics */}
        <section>
          <GrowthChart
            data={metrics.growth_trends || []}
            platformBreakdown={metrics.platform_breakdown || {}}
          />
        </section>

        {/* Monetization Milestones & AI Optimization Tips */}
        <section>
          <MonetizationTips
            overview={overview}
            recommendations={metrics.optimization_recommendations || []}
          />
        </section>

        {/* Video Table & Performance Logs */}
        <section>
          <VideoTable videos={history} />
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>
            Autonomous Social Video Agent • Diseñado para costo $0 en GitHub Actions & Pages
          </span>
          <span className="font-mono text-slate-400">
            Stack: Python 3.12 • MoviePy • Edge-TTS • Vite • React 19 • Tailwind CSS
          </span>
        </div>
      </footer>
    </div>
  );
}
