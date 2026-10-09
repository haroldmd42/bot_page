import React, { useState, useEffect } from 'react';
import {
  X,
  Play,
  Sparkles,
  Key,
  ExternalLink,
  CheckCircle2,
  AlertCircle,
  Copy,
  Terminal,
  ShieldCheck,
  Send
} from 'lucide-react';

export default function TriggerBotModal({ isOpen, onClose, repoOwner = 'haroldmd42', repoName = 'bot_page' }) {
  const [topic, setTopic] = useState('');
  const [videoCount, setVideoCount] = useState('3');
  const [githubToken, setGithubToken] = useState('');
  const [saveToken, setSaveToken] = useState(true);
  const [status, setStatus] = useState('idle'); // 'idle' | 'loading' | 'success' | 'error'
  const [statusMessage, setStatusMessage] = useState('');
  const [copied, setCopied] = useState(false);

  // Load token from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('gh_pat_token');
    if (saved) {
      setGithubToken(saved);
    }
  }, []);

  if (!isOpen) return null;

  const handleTrigger = async (e) => {
    e.preventDefault();
    if (!githubToken.trim()) {
      setStatus('error');
      setStatusMessage('Ingresa tu GitHub Personal Access Token para disparar el bot directamente desde el navegador.');
      return;
    }

    if (saveToken) {
      localStorage.setItem('gh_pat_token', githubToken.trim());
    } else {
      localStorage.removeItem('gh_pat_token');
    }

    setStatus('loading');
    setStatusMessage(`Enviando orden a GitHub Actions para publicar ${videoCount} videos...`);

    try {
      const url = `https://api.github.com/repos/${repoOwner}/${repoName}/actions/workflows/auto_publish.yml/dispatches`;
      const payload = {
        ref: 'main',
        inputs: {
          count: videoCount,
          topic: topic.trim() || '',
          dry_run: false
        }
      };

      const res = await fetch(url, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${githubToken.trim()}`,
          Accept: 'application/vnd.github.v3+json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (res.status === 204 || res.ok) {
        setStatus('success');
        setStatusMessage('¡El Agente ha comenzado a ejecutarse en GitHub Actions! Creará y publicará el video en unos instantes.');
      } else {
        const errorData = await res.json().catch(() => ({}));
        setStatus('error');
        setStatusMessage(errorData.message || `Error ${res.status}: Verifica que tu token tenga permisos 'workflow' o 'repo'.`);
      }
    } catch (err) {
      setStatus('error');
      setStatusMessage(`Error de conexión: ${err.message}`);
    }
  };

  const copyCommand = () => {
    const cmd = topic.trim()
      ? `python bot/main.py --mode publish --topic "${topic.trim()}"`
      : 'python bot/main.py --mode publish';
    navigator.clipboard.writeText(cmd);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-800 bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-yellow-400/20 text-yellow-400 border border-yellow-400/30">
              <Play className="w-5 h-5 fill-yellow-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white font-display">
                Ejecutar Agente Manualmente
              </h3>
              <p className="text-xs text-slate-400">
                Dispara la creación, renderizado y publicación de un nuevo video
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 overflow-y-auto">
          {/* Topic Input */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-yellow-400" />
              Tema o Título Cómico (Opcional)
            </label>
            <input
              type="text"
              placeholder="Ej: Gatos dramáticos haciendo drama total (o déjalo vacío para IA automática)"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-yellow-400"
            />
            <p className="text-[11px] text-slate-400 mt-1">
              Si lo dejas vacío, el <strong>Growth Optimizer</strong> seleccionará clips cómicos y ganchos de alta retención.
            </p>
          </div>

          {/* Video Count Selector */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-1.5 flex items-center gap-1.5">
              <Play className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
              Cantidad de Videos a Generar:
            </label>
            <div className="grid grid-cols-3 gap-2">
              {['1', '2', '3'].map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setVideoCount(num)}
                  className={`py-2 px-3 rounded-xl text-xs font-bold border transition-all ${
                    videoCount === num
                      ? 'bg-yellow-400 text-slate-950 border-yellow-400 shadow-md shadow-yellow-500/20'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  {num} {num === '1' ? 'Video' : 'Videos'} {num === '3' ? '🔥' : ''}
                </button>
              ))}
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              Generará {videoCount} videos únicos con clips cómicos y remates totalmente diferentes.
            </p>
          </div>

          {/* Method 1: Direct 1-Click via Token */}
          <form onSubmit={handleTrigger} className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-yellow-400 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5" />
                Opción A: Disparo Directo desde el Dashboard
              </span>
              <a
                href="https://github.com/settings/tokens/new?scopes=repo,workflow&description=ViralAgentDashboard"
                target="_blank"
                rel="noreferrer"
                className="text-[10px] text-blue-400 hover:text-blue-300 flex items-center gap-1"
              >
                Crear Token en GitHub <ExternalLink className="w-2.5 h-2.5" />
              </a>
            </div>

            <input
              type="password"
              placeholder="Pega tu GitHub Token (PAT con permiso 'workflow')"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-yellow-400"
            />

            <div className="flex items-center justify-between text-[11px]">
              <label className="flex items-center gap-2 text-slate-400 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={saveToken}
                  onChange={(e) => setSaveToken(e.target.checked)}
                  className="rounded bg-slate-900 border-slate-700 text-yellow-400 focus:ring-0"
                />
                Guardar en mi navegador (LocalStorage privado)
              </label>
              <span className="text-slate-500 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3 text-emerald-400" /> 100% Seguro
              </span>
            </div>

            <button
              type="submit"
              disabled={status === 'loading'}
              className="w-full mt-2 bg-yellow-400 hover:bg-yellow-300 text-slate-950 font-bold py-2.5 px-4 rounded-xl text-xs flex items-center justify-center gap-2 transition-all shadow-md shadow-yellow-500/10 disabled:opacity-50"
            >
              {status === 'loading' ? (
                <span>Lanzando Agente...</span>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
                  <span>🚀 Generar y Publicar Ahora en YouTube</span>
                </>
              )}
            </button>
          </form>

          {/* Status Feedback */}
          {status === 'success' && (
            <div className="bg-emerald-500/10 border border-emerald-500/30 p-3.5 rounded-xl text-xs text-emerald-400 space-y-2">
              <div className="flex items-center gap-2 font-bold">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>{statusMessage}</span>
              </div>
              <a
                href={`https://github.com/${repoOwner}/${repoName}/actions`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-[11px] font-bold text-white bg-emerald-600 hover:bg-emerald-500 px-3 py-1 rounded-lg transition-colors"
              >
                Ver Ejecución en Vivo en GitHub Actions <ExternalLink className="w-3 h-3 ml-1" />
              </a>
            </div>
          )}

          {status === 'error' && (
            <div className="bg-rose-500/10 border border-rose-500/30 p-3.5 rounded-xl text-xs text-rose-400 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{statusMessage}</span>
            </div>
          )}

          {/* Method 2: Fallback direct button to GitHub Actions */}
          <div className="pt-2 border-t border-slate-800 space-y-3">
            <span className="text-xs font-bold text-slate-300 block">
              Opción B: Sin Token (Directo en la web de GitHub)
            </span>
            <a
              href={`https://github.com/${repoOwner}/${repoName}/actions/workflows/auto_publish.yml`}
              target="_blank"
              rel="noreferrer"
              className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold py-2 px-4 rounded-xl text-xs flex items-center justify-center gap-2 transition-colors border border-slate-700"
            >
              <span>Abrir pestaña de GitHub Actions (Botón "Run workflow")</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>

            {/* Method 3: Copy terminal command */}
            <div className="flex items-center justify-between bg-slate-950 p-2.5 rounded-xl border border-slate-800 text-[11px]">
              <span className="text-slate-400 font-mono flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-yellow-400" />
                Comando local:
              </span>
              <button
                type="button"
                onClick={copyCommand}
                className="text-yellow-400 hover:text-yellow-300 flex items-center gap-1 font-semibold"
              >
                <Copy className="w-3 h-3" />
                {copied ? '¡Copiado!' : 'Copiar comando'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
