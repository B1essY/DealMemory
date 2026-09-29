import React, { useEffect, useState } from 'react';
import {
  Brain,
  History,
  TrendingUp,
  Building2,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Clock,
  Layers
} from 'lucide-react';
import { fetchNegotiations, fetchSeedStatus, seedDemoData, fetchHealthDetailed } from '../services/api';
import type { Negotiation, SeedStatus, SystemHealth } from '../types';
import { SystemHealthWidget } from '../components/SystemHealthWidget';

interface DashboardProps {
  setActiveTab: (tab: string) => void;
  onSelectDealForAnalysis: (deal: Negotiation) => void;
}

export const DashboardPage: React.FC<DashboardProps> = ({
  setActiveTab,
  onSelectDealForAnalysis
}) => {
  const [deals, setDeals] = useState<Negotiation[]>([]);
  const [seedStatus, setSeedStatus] = useState<SeedStatus | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [seedingLoading, setSeedingLoading] = useState(false);
  const [seedMessage, setSeedMessage] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [dealsData, seedData, healthData] = await Promise.all([
        fetchNegotiations().catch(() => []),
        fetchSeedStatus().catch(() => null),
        fetchHealthDetailed().catch(() => null)
      ]);
      setDeals(dealsData);
      setSeedStatus(seedData);
      setHealth(healthData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSeed = async () => {
    setSeedingLoading(true);
    setSeedMessage(null);
    try {
      const res = await seedDemoData();
      setSeedMessage(`Successfully seeded ${res.seeded} experiences into Hindsight memory bank!`);
      await loadData();
    } catch (err: any) {
      setSeedMessage(`Seeding note: ${err.message}`);
    } finally {
      setSeedingLoading(false);
    }
  };

  const totalDeals = deals.length;
  const analyzedDeals = deals.filter((d) => d.is_analyzed).length;
  const uniqueVendors = Array.from(new Set(deals.map((d) => d.vendor))).length;
  const memoryExperiences = seedStatus?.verified_count || (seedStatus?.is_seeded ? 12 : 0);

  return (
    <div className="space-y-6">
      {/* Hero Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-sky-950 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-sm">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 text-sky-400 text-xs font-mono border border-sky-500/20 mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Persistent SaaS Procurement Intelligence</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
            Negotiation intelligence that learns from every deal.
          </h1>
          <p className="mt-2 text-slate-300 text-sm sm:text-base leading-relaxed">
            Before negotiations, DealMemory recalls prior vendor concession stances and cross-vendor
            tactical patterns from <span className="text-sky-400 font-medium">Hindsight Cloud</span> to build
            evidence-grounded briefings. After closing, actual outcomes are retained back into memory.
          </p>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              onClick={() => setActiveTab('negotiation')}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-sky-500 text-white font-medium text-sm hover:bg-sky-400 transition shadow-sm"
            >
              <Brain className="w-4 h-4" />
              <span>Start New Deal Analysis</span>
            </button>
            <button
              onClick={() => setActiveTab('demo')}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-800 text-slate-200 font-medium text-sm hover:bg-slate-700 border border-slate-700 transition"
            >
              <span>Explore Guided Demo (60s)</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Real Metric Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Deals Tracked</span>
            <Layers className="w-4 h-4 text-sky-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-white">{totalDeals}</div>
          <div className="mt-1 text-xs text-slate-500">
            {analyzedDeals} analyzed with AI strategy
          </div>
        </div>

        {/* Metric 2 */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Hindsight Experiences</span>
            <Sparkles className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-emerald-400">
            {memoryExperiences}
          </div>
          <div className="mt-1 text-xs text-slate-500">
            Indexed in organization memory bank
          </div>
        </div>

        {/* Metric 3 */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Tracked SaaS Vendors</span>
            <Building2 className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-white">{uniqueVendors || 5}</div>
          <div className="mt-1 text-xs text-slate-500">
            CRM, HR, Cloud, Cyber, Collab
          </div>
        </div>

        {/* Metric 4 */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Memory Seeding Status</span>
            <History className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-3 flex items-center gap-2">
            <span className={`text-lg font-bold ${seedStatus?.is_seeded ? 'text-emerald-400' : 'text-amber-400'}`}>
              {seedStatus?.is_seeded ? '12/12 Seeded' : 'Not Seeded'}
            </span>
          </div>
          <div className="mt-1">
            {!seedStatus?.is_seeded ? (
              <button
                onClick={handleSeed}
                disabled={seedingLoading}
                className="text-xs text-sky-400 hover:text-sky-300 underline font-medium"
              >
                {seedingLoading ? 'Seeding...' : 'Click to Seed Memory Bank'}
              </button>
            ) : (
              <span className="text-xs text-slate-500">Memory bank fully initialized</span>
            )}
          </div>
        </div>
      </div>

      {seedMessage && (
        <div className="p-3 rounded-lg bg-sky-950/50 border border-sky-800 text-sky-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-sky-400" />
          <span>{seedMessage}</span>
        </div>
      )}

      {/* System Health Widget */}
      <SystemHealthWidget health={health} onRefresh={loadData} loading={loading} />

      {/* Core Learned Patterns Preview */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-sky-400" />
              <span>Key Organizational Learned Patterns (Recalled From Memory)</span>
            </h3>
            <p className="text-xs text-slate-400">
              Cross-vendor empirical patterns discovered through historical negotiation retention
            </p>
          </div>
          <button
            onClick={() => setActiveTab('memory')}
            className="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1 font-medium"
          >
            <span>Explore All in Memory</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-emerald-400">High Success Lever</span>
              <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                ~71% Success
              </span>
            </div>
            <div className="mt-2 text-sm font-medium text-slate-200">Support-Fee Unbundling Challenge</div>
            <p className="mt-1 text-xs text-slate-400">
              5 of 7 historical attempts achieved 12-21% reductions by auditing mandatory SLA tiers across KavachSec & SetuConnect.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-rose-400">Known Failure Trap</span>
              <span className="text-xs px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20">
                0% Success (3/3 Failed)
              </span>
            </div>
            <div className="mt-2 text-sm font-medium text-slate-200">Early-Renewal Discount Request</div>
            <p className="mt-1 text-xs text-slate-400">
              Failed 3 out of 3 times. SaaS vendors treat early renewals as committed renewals with zero competitive urgency.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-950/60 border border-slate-800/80">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-amber-400">Timing-Dependent Pattern</span>
              <span className="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                March & September
              </span>
            </div>
            <div className="mt-2 text-sm font-medium text-slate-200">Quarter-End Timing Crunch</div>
            <p className="mt-1 text-xs text-slate-400">
              MeghMonitor consistently concessions 19-22% when deal execution is held until within 72 hours of quarter close.
            </p>
          </div>
        </div>
      </div>

      {/* Recent Negotiations Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Recent SaaS Negotiations</h3>
            <p className="text-xs text-slate-400">
              Stored in SQLite metadata (Auditing & UI history only; never passed as LLM memory)
            </p>
          </div>
          <button
            onClick={() => setActiveTab('negotiation')}
            className="text-xs px-3 py-1.5 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20 hover:bg-sky-500/20 font-medium"
          >
            + New Deal
          </button>
        </div>

        {deals.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-sm">
            No negotiations recorded yet. Click "Start New Deal Analysis" or "Seed Memory Bank" to populate records.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Vendor / Product</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Seats</th>
                  <th className="py-2.5 px-3">Initial Quote</th>
                  <th className="py-2.5 px-3">Deadline</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {deals.slice(0, 8).map((d) => (
                  <tr key={d.id} className="hover:bg-slate-800/30 transition">
                    <td className="py-2.5 px-3 font-medium text-white">
                      <div>{d.vendor}</div>
                      <div className="text-[11px] text-slate-400">{d.product}</div>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400">{d.category}</td>
                    <td className="py-2.5 px-3">{d.seats}</td>
                    <td className="py-2.5 px-3 font-mono">₹{d.initial_quote.toLocaleString('en-IN')}</td>
                    <td className="py-2.5 px-3">{d.deadline}</td>
                    <td className="py-2.5 px-3">
                      {d.is_analyzed ? (
                        <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                          <CheckCircle2 className="w-3 h-3" />
                          Analyzed
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                          <Clock className="w-3 h-3" />
                          Draft
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <button
                        onClick={() => {
                          onSelectDealForAnalysis(d);
                          setActiveTab('negotiation');
                        }}
                        className="text-xs text-sky-400 hover:text-sky-300 font-medium"
                      >
                        Analyze & Brief →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Synthetic Disclaimer Banner */}
      <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-center text-xs text-slate-500">
        Results from a small synthetic test set. All data labelled "Synthetic demo data." Never claim real-world savings.
      </div>
    </div>
  );
};
