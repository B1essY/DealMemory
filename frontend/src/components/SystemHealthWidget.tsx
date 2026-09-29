import React from 'react';
import { CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import type { SystemHealth } from '../types';

interface HealthWidgetProps {
  health: SystemHealth | null;
  onRefresh: () => void;
  loading?: boolean;
}

export const SystemHealthWidget: React.FC<HealthWidgetProps> = ({ health, onRefresh, loading }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">System Architecture & Status</h3>
          <p className="text-xs text-slate-400">Real-time health of local metadata, Hindsight Cloud, and LLM</p>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded transition"
          title="Refresh Status"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* SQLite */}
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 flex items-start gap-3">
          {health?.services.sqlite.status === 'connected' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          )}
          <div>
            <div className="text-xs font-medium text-slate-300">SQLite Database</div>
            <div className="text-xs text-slate-400 mt-0.5">
              {health?.services.sqlite.message || 'Connecting...'}
            </div>
            <div className="text-[10px] text-slate-500 mt-1">App metadata & eval only</div>
          </div>
        </div>

        {/* Hindsight */}
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 flex items-start gap-3">
          {health?.services.hindsight.status === 'connected' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          )}
          <div>
            <div className="text-xs font-medium text-slate-300">Hindsight Memory Bank</div>
            <div className="text-xs text-slate-400 mt-0.5">
              {health?.services.hindsight.message || 'Connecting...'}
            </div>
            <div className="text-[10px] text-sky-400 mt-1">Sole organizational memory</div>
          </div>
        </div>

        {/* Groq */}
        <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 flex items-start gap-3">
          {health?.services.groq.status === 'connected' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          )}
          <div>
            <div className="text-xs font-medium text-slate-300">Groq LLM Engine</div>
            <div className="text-xs text-slate-400 mt-0.5">
              {health?.services.groq.message || 'Connecting...'}
            </div>
            <div className="text-[10px] text-slate-500 mt-1">Fast inference with Pydantic JSON</div>
          </div>
        </div>
      </div>
    </div>
  );
};
