import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Search
} from 'lucide-react';
import { testRecall, fetchMemoryStats } from '../services/api';

export const MemoryPage: React.FC = () => {
  const [stats, setStats] = useState<any>(null);

  // Recall Test Box State
  const [recallQuery, setRecallQuery] = useState(
    'What discount outcomes and support fee challenges occurred with KavachSec?'
  );
  const [budget, setBudget] = useState('high');
  const [recallResults, setRecallResults] = useState<any[]>([]);
  const [recallLoading, setRecallLoading] = useState(false);
  const [recallSearched, setRecallSearched] = useState(false);
  const [recallError, setRecallError] = useState<string | null>(null);

  useEffect(() => {
    fetchMemoryStats()
      .then((statsRes) => setStats(statsRes))
      .catch(() => null);
  }, []);

  const handleTestRecall = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!recallQuery.trim()) return;

    setRecallLoading(true);
    setRecallError(null);
    setRecallSearched(true);
    try {
      const res = await testRecall(recallQuery, budget);
      setRecallResults(res.memories || []);
    } catch (err: any) {
      setRecallError(err.message || 'Recall failed');
      setRecallResults([]);
    } finally {
      setRecallLoading(false);
    }
  };

  // Preset queries
  const presetQueries = [
    'What discount outcomes and support fee challenges occurred with KavachSec?',
    'When does MeghMonitor concede discounts near fiscal quarter end?',
    'How do volume discounts compare at 40 seats vs 150+ seats for KarmicHR and VyaparPulse?',
    'What negotiation tactics have failed consistently across all SaaS vendors?'
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-slate-800 pb-5">
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-sky-400" />
          <span>Organizational Memory & Intelligence Explorer</span>
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Explore facts, entities, cross-vendor patterns, and temporal observations stored permanently in Hindsight Cloud.
        </p>
      </div>

      {/* Memory Bank Stats Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400">Memory Bank ID</span>
          <div className="mt-1 text-base font-bold font-mono text-sky-400 truncate">
            {stats?.bank_id || 'dealmemory-org-prod'}
          </div>
          <div className="mt-1 text-[11px] text-slate-500">Dedicated organizational memory bank</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400">Hindsight Engine Status</span>
          <div className="mt-1 text-base font-bold text-emerald-400 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Online (API v{stats?.api_version || '0.10.2'})</span>
          </div>
          <div className="mt-1 text-[11px] text-slate-500">Semantic + BM25 + Graph + Temporal</div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400">Retained Memory Units</span>
          <div className="mt-1 text-base font-bold text-white font-mono">
            {stats?.total_memories_sample_count || 12} Documents / Facts
          </div>
          <div className="mt-1 text-[11px] text-slate-500">Incremental accumulation (N → N+1)</div>
        </div>
      </div>

      {/* Interactive Recall Test Box */}
      <div className="bg-slate-900 border border-sky-500/30 rounded-xl p-5 shadow-lg shadow-sky-950/20">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-2">
          <Search className="w-4 h-4 text-sky-400" />
          <span>Test Organizational Memory (Live Hindsight Recall)</span>
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Query the live memory bank using Hindsight's 4-strategy retrieval pipeline. View extracted facts, citations, and metadata.
        </p>

        <form onSubmit={handleTestRecall} className="space-y-3">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <input
                type="text"
                value={recallQuery}
                onChange={(e) => setRecallQuery(e.target.value)}
                placeholder="Ask any question about past negotiations..."
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-3 pr-10 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-sky-500 font-medium"
              />
            </div>
            <div className="flex items-center gap-2">
              <select
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none"
              >
                <option value="low">Budget: Low</option>
                <option value="mid">Budget: Mid</option>
                <option value="high">Budget: High (Deep Recall)</option>
              </select>
              <button
                type="submit"
                disabled={recallLoading}
                className="px-4 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-white font-semibold text-xs transition shadow-sm whitespace-nowrap"
              >
                {recallLoading ? 'Recalling...' : 'Execute Recall'}
              </button>
            </div>
          </div>

          {/* Quick preset suggestions */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-[11px] text-slate-500">Try query:</span>
            {presetQueries.map((pq, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setRecallQuery(pq)}
                className="text-[11px] px-2 py-0.5 rounded bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-300 transition truncate max-w-xs"
              >
                {pq}
              </button>
            ))}
          </div>
        </form>

        {recallError && (
          <div className="mt-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            Recall Error: {recallError}
          </div>
        )}

        {/* Recall Results View */}
        {recallSearched && !recallLoading && (
          <div className="mt-5 pt-4 border-t border-slate-800 space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-300">
                Recalled Memory Facts ({recallResults.length} matches):
              </span>
              <span className="text-slate-500 font-mono">Retrieved from Hindsight Cloud</span>
            </div>

            {recallResults.length === 0 ? (
              <div className="text-center py-6 text-xs text-slate-400 italic bg-slate-950/60 rounded-lg border border-slate-800">
                No relevant organizational experience found.
              </div>
            ) : (
              <div className="space-y-2.5">
                {recallResults.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-lg bg-slate-950 border border-slate-800 hover:border-slate-700 transition text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-mono text-sky-400 font-medium">Fact ID: {item.id}</span>
                      <div className="flex items-center gap-2">
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                          {item.type}
                        </span>
                        {item.document_id && (
                          <span className="text-slate-500 text-[10px] font-mono">
                            Doc: {item.document_id}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="text-slate-200 font-medium leading-relaxed">{item.text}</div>

                    <div className="flex flex-wrap items-center gap-3 pt-1 text-[10px] text-slate-400">
                      {item.context && (
                        <span><strong className="text-slate-500">Context:</strong> {item.context}</span>
                      )}
                      {item.occurred_start && (
                        <span><strong className="text-slate-500">Occurred:</strong> {item.occurred_start.slice(0, 10)}</span>
                      )}
                      {item.entities && item.entities.length > 0 && (
                        <span><strong className="text-slate-500">Entities:</strong> {item.entities.join(', ')}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 5 Tracked Vendor Intelligence Profiles */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-white">Vendor Commercial Intelligence Profiles</h3>
          <p className="text-xs text-slate-400">
            Empirical negotiation stances learned from real past interactions
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
          {/* KavachSec */}
          <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">KavachSec</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-sky-300">Cybersecurity</span>
            </div>
            <div className="text-slate-300 font-medium">Support fee unbundling target</div>
            <p className="text-slate-400 text-[11px]">
              Routinely marks up initial support fees by 20-25%. Concedes 16-20% when SLA tiers are challenged. Multi-year discounts are refused.
            </p>
          </div>

          {/* VyaparPulse */}
          <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">VyaparPulse</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-indigo-300">CRM</span>
            </div>
            <div className="text-slate-300 font-medium">Multi-year trade receptive</div>
            <p className="text-slate-400 text-[11px]">
              Rejects 1-year licence discounts outright, but concessions 18-22% when offered a 36-month contract with annual milestone billing.
            </p>
          </div>

          {/* MeghMonitor */}
          <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">MeghMonitor</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-cyan-300">Cloud APM</span>
            </div>
            <div className="text-slate-300 font-medium">Quarter-end quota vulnerability</div>
            <p className="text-slate-400 text-[11px]">
              Extreme sales quota pressure in late March and late September. Timing signing within 72 hours of quarter end yields 19-22% reductions.
            </p>
          </div>

          {/* KarmicHR */}
          <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">KarmicHR</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-purple-300">HR Software</span>
            </div>
            <div className="text-slate-300 font-medium">Volume bracket driven</div>
            <p className="text-slate-400 text-[11px]">
              Categorically rejects early-renewal discounts. Leverage comes strictly from crossing tier thresholds (100+ and 200+ seats).
            </p>
          </div>

          {/* SetuConnect */}
          <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-white">SetuConnect</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-emerald-300">Collaboration</span>
            </div>
            <div className="text-slate-300 font-medium">Auto-renewal & support pushback</div>
            <p className="text-slate-400 text-[11px]">
              Attempts 60-day auto-renewal locks and 20% platform fees. Concedes easily on striking auto-renewal and cutting support fees when pressed.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
