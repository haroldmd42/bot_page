import React, { useState } from 'react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { BarChart3, TrendingUp, Layers } from 'lucide-react';

export default function GrowthChart({ data = [], platformBreakdown = {} }) {
  const [activeTab, setActiveTab] = useState('views'); // 'views' | 'engagement' | 'platforms'

  const formatNumber = (num) => {
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
    return num;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900/95 backdrop-blur-md border border-slate-700/80 rounded-xl p-3.5 shadow-2xl text-xs space-y-1.5 min-w-[170px]">
          <p className="font-bold text-slate-200 border-b border-slate-700/60 pb-1 mb-2">
            📅 {label}
          </p>
          {payload.map((item, idx) => (
            <div key={idx} className="flex justify-between items-center space-x-3">
              <span className="flex items-center space-x-1.5" style={{ color: item.color }}>
                <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: item.color }}></span>
                <span>{item.name}:</span>
              </span>
              <span className="font-bold text-white">
                {typeof item.value === 'number' ? item.value.toLocaleString() : item.value}
                {item.name.includes('%') ? '%' : ''}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  const platformData = [
    {
      name: 'Facebook Reels',
      views: platformBreakdown?.facebook?.views || 347400,
      share: platformBreakdown?.facebook?.share_pct || 53.9,
      fill: '#3B82F6'
    },
    {
      name: 'YouTube Shorts',
      views: platformBreakdown?.youtube?.views || 297000,
      share: platformBreakdown?.youtube?.share_pct || 46.1,
      fill: '#EF4444'
    }
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-lg font-bold text-white font-display flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-yellow-400" />
            Curva de Crecimiento & Rendimiento
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Métricas sincronizadas automáticamente desde las APIs oficiales de Meta y YouTube
          </p>
        </div>

        {/* Tab Selector */}
        <div className="inline-flex rounded-xl bg-slate-800/80 p-1 border border-slate-700/60 self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('views')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'views'
                ? 'bg-yellow-400 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Reproducciones
          </button>
          <button
            onClick={() => setActiveTab('engagement')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'engagement'
                ? 'bg-yellow-400 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Interacción
          </button>
          <button
            onClick={() => setActiveTab('platforms')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'platforms'
                ? 'bg-yellow-400 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Plataformas
          </button>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {activeTab === 'views' ? (
            <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="viewsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#FACC15" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#FACC15" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="cumViewsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey="date" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} tickFormatter={formatNumber} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Area
                type="monotone"
                dataKey="cumulative_views"
                name="Vistas Acumuladas"
                stroke="#8B5CF6"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#cumViewsGradient)"
              />
              <Area
                type="monotone"
                dataKey="views"
                name="Vistas por Día"
                stroke="#FACC15"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#viewsGradient)"
              />
            </AreaChart>
          ) : activeTab === 'engagement' ? (
            <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey="date" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748B" fontSize={11} tickFormatter={formatNumber} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
              <Bar dataKey="likes" name="Likes" fill="#EF4444" radius={[6, 6, 0, 0]} />
              <Bar dataKey="comments" name="Comentarios" fill="#3B82F6" radius={[6, 6, 0, 0]} />
              <Bar dataKey="shares" name="Compartidos" fill="#10B981" radius={[6, 6, 0, 0]} />
            </BarChart>
          ) : (
            <BarChart data={platformData} layout="vertical" margin={{ top: 10, right: 30, left: 30, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
              <XAxis type="number" stroke="#64748B" fontSize={11} tickFormatter={formatNumber} />
              <YAxis dataKey="name" type="category" stroke="#94A3B8" fontSize={12} width={110} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="views" name="Vistas Totales" radius={[0, 8, 8, 0]}>
                {platformData.map((entry, index) => (
                  <Bar key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
