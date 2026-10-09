import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function MetricCard({
  title,
  value,
  subValue,
  icon: Icon,
  trend,
  trendDirection = 'up',
  colorScheme = 'yellow'
}) {
  const colorMap = {
    yellow: {
      border: 'border-yellow-500/20 hover:border-yellow-500/40',
      iconBg: 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30',
      glow: 'hover:shadow-[0_0_30px_rgba(250,204,21,0.15)]'
    },
    blue: {
      border: 'border-blue-500/20 hover:border-blue-500/40',
      iconBg: 'bg-blue-500/10 text-blue-400 border border-blue-500/30',
      glow: 'hover:shadow-[0_0_30px_rgba(59,130,246,0.15)]'
    },
    purple: {
      border: 'border-purple-500/20 hover:border-purple-500/40',
      iconBg: 'bg-purple-500/10 text-purple-400 border border-purple-500/30',
      glow: 'hover:shadow-[0_0_30px_rgba(139,92,246,0.15)]'
    },
    emerald: {
      border: 'border-emerald-500/20 hover:border-emerald-500/40',
      iconBg: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30',
      glow: 'hover:shadow-[0_0_30px_rgba(16,185,129,0.15)]'
    },
    red: {
      border: 'border-rose-500/20 hover:border-rose-500/40',
      iconBg: 'bg-rose-500/10 text-rose-400 border border-rose-500/30',
      glow: 'hover:shadow-[0_0_30px_rgba(244,63,94,0.15)]'
    }
  };

  const style = colorMap[colorScheme] || colorMap.yellow;

  return (
    <div
      className={`glass-panel rounded-2xl p-6 transition-all duration-300 ${style.border} ${style.glow} relative overflow-hidden group`}
    >
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs uppercase tracking-wider font-semibold text-slate-400">
          {title}
        </span>
        {Icon && (
          <div className={`p-2.5 rounded-xl transition-transform duration-300 group-hover:scale-110 ${style.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="flex items-baseline space-x-2">
        <h3 className="text-3xl font-black text-white font-display tracking-tight">
          {value}
        </h3>
        {subValue && (
          <span className="text-xs text-slate-400 font-medium">
            {subValue}
          </span>
        )}
      </div>

      {trend && (
        <div className="mt-3 flex items-center space-x-1.5 text-xs font-semibold">
          {trendDirection === 'up' ? (
            <span className="inline-flex items-center text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
              <TrendingUp className="w-3.5 h-3.5 mr-1" />
              {trend}
            </span>
          ) : (
            <span className="inline-flex items-center text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-md border border-rose-500/20">
              <TrendingDown className="w-3.5 h-3.5 mr-1" />
              {trend}
            </span>
          )}
          <span className="text-slate-500 text-[11px]">vs. periodo anterior</span>
        </div>
      )}

      {/* Decorative corner ambient glow */}
      <div className="absolute -right-8 -bottom-8 w-24 h-24 rounded-full bg-white/5 blur-2xl pointer-events-none group-hover:bg-white/10 transition-colors" />
    </div>
  );
}
