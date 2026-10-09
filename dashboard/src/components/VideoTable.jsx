import React, { useState } from 'react';
import {
  ExternalLink,
  Play,
  Heart,
  MessageCircle,
  Share2,
  Eye,
  Filter,
  Search,
  CheckCircle,
  Clock
} from 'lucide-react';

export default function VideoTable({ videos = [] }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNiche, setSelectedNiche] = useState('ALL');

  const niches = ['ALL', ...new Set(videos.map((v) => v.niche).filter(Boolean))];

  const filteredVideos = videos.filter((v) => {
    const matchesSearch =
      v.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (v.hook && v.hook.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesNiche = selectedNiche === 'ALL' || v.niche === selectedNiche;
    return matchesSearch && matchesNiche;
  });

  const formatNumber = (num) => {
    if (!num) return '0';
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
    return num.toLocaleString();
  };

  const formatDate = (isoStr) => {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('es-ES', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800">
      {/* Header and Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-lg font-bold text-white font-display flex items-center gap-2">
            <Play className="w-5 h-5 text-yellow-400 fill-yellow-400" />
            Registro de Videos Publicados ({filteredVideos.length})
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Monitoreo en vivo de publicaciones con enlaces directos a Reels y Shorts
          </p>
        </div>

        {/* Filter and Search Bar */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Buscar título o gancho..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-900 border border-slate-700/80 rounded-xl pl-9 pr-3.5 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-yellow-400 w-52 sm:w-64"
            />
          </div>

          <div className="flex items-center gap-1 bg-slate-900 border border-slate-700/80 rounded-xl px-2.5 py-1 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400 mr-1" />
            <select
              value={selectedNiche}
              onChange={(e) => setSelectedNiche(e.target.value)}
              className="bg-transparent text-slate-300 focus:outline-none text-xs cursor-pointer"
            >
              {niches.map((n) => (
                <option key={n} value={n} className="bg-slate-900 text-slate-200">
                  {n === 'ALL' ? 'Todos los Nichos' : n}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Table / List */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[700px]">
          <thead>
            <tr className="border-b border-slate-800 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              <th className="py-3 px-3">Video & Gancho</th>
              <th className="py-3 px-3 text-center">Nicho</th>
              <th className="py-3 px-3 text-center">Fecha</th>
              <th className="py-3 px-3 text-center">YouTube Shorts</th>
              <th className="py-3 px-3 text-center">Facebook Reels</th>
              <th className="py-3 px-3 text-center">Total Vistas</th>
              <th className="py-3 px-3 text-center">Engagement</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {filteredVideos.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500 text-xs">
                  No se encontraron videos coincidentes.
                </td>
              </tr>
            ) : (
              filteredVideos.map((video) => (
                <tr
                  key={video.id}
                  className="hover:bg-slate-800/30 transition-colors group"
                >
                  {/* Title & Hook */}
                  <td className="py-4 px-3 max-w-xs">
                    <div className="font-semibold text-slate-100 group-hover:text-yellow-400 transition-colors leading-snug">
                      {video.title}
                    </div>
                    {video.hook && (
                      <div className="text-[11px] text-slate-400 italic mt-1 line-clamp-1">
                        "{video.hook}"
                      </div>
                    )}
                  </td>

                  {/* Niche */}
                  <td className="py-4 px-3 text-center whitespace-nowrap">
                    <span className="inline-block bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded-md text-[10px] font-semibold">
                      {video.niche || 'General'}
                    </span>
                  </td>

                  {/* Date */}
                  <td className="py-4 px-3 text-center text-slate-400 whitespace-nowrap text-[11px]">
                    {formatDate(video.created_at)}
                  </td>

                  {/* YouTube Platform column */}
                  <td className="py-4 px-3 text-center whitespace-nowrap">
                    <div className="inline-flex flex-col items-center">
                      <div className="flex items-center gap-1.5 font-bold text-slate-200">
                        <Eye className="w-3.5 h-3.5 text-rose-500" />
                        <span>{formatNumber(video.youtube?.views)}</span>
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-0.5">
                        <span className="flex items-center gap-0.5">
                          <Heart className="w-2.5 h-2.5 text-rose-400" />
                          {formatNumber(video.youtube?.likes)}
                        </span>
                        <span className="flex items-center gap-0.5">
                          <MessageCircle className="w-2.5 h-2.5 text-slate-400" />
                          {formatNumber(video.youtube?.comments)}
                        </span>
                      </div>
                      {video.youtube?.url && (
                        <a
                          href={video.youtube.url}
                          target="_blank"
                          rel="noreferrer"
                          className="mt-1.5 inline-flex items-center gap-1 text-[10px] text-rose-400 hover:text-rose-300 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20"
                        >
                          Ver Short <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                    </div>
                  </td>

                  {/* Facebook Platform column */}
                  <td className="py-4 px-3 text-center whitespace-nowrap">
                    <div className="inline-flex flex-col items-center">
                      <div className="flex items-center gap-1.5 font-bold text-slate-200">
                        <Eye className="w-3.5 h-3.5 text-blue-500" />
                        <span>{formatNumber(video.facebook?.views)}</span>
                      </div>
                      <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-0.5">
                        <span className="flex items-center gap-0.5">
                          <Heart className="w-2.5 h-2.5 text-blue-400" />
                          {formatNumber(video.facebook?.likes)}
                        </span>
                        <span className="flex items-center gap-0.5">
                          <Share2 className="w-2.5 h-2.5 text-emerald-400" />
                          {formatNumber(video.facebook?.shares)}
                        </span>
                      </div>
                      {video.facebook?.url ? (
                        <a
                          href={video.facebook.url}
                          target="_blank"
                          rel="noreferrer"
                          className="mt-1.5 inline-flex items-center gap-1 text-[10px] text-blue-400 hover:text-blue-300 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20"
                        >
                          Ver Reel <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      ) : (
                        <span className="mt-1.5 inline-block text-[10px] text-slate-500 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">
                          Pendiente
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Total Views */}
                  <td className="py-4 px-3 text-center whitespace-nowrap">
                    <span className="font-extrabold text-sm text-yellow-400">
                      {formatNumber(video.metrics_summary?.total_views)}
                    </span>
                  </td>

                  {/* Engagement Rate */}
                  <td className="py-4 px-3 text-center whitespace-nowrap">
                    <span
                      className={`inline-block px-2 py-0.5 rounded-full text-[11px] font-bold ${
                        (video.metrics_summary?.engagement_rate || 0) >= 10
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                      }`}
                    >
                      {video.metrics_summary?.engagement_rate || 0}%
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
