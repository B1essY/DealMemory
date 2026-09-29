import React, { useState, useEffect } from 'react';
import {
  PlayCircle,
  CheckCircle2,
  RefreshCw,
  ChevronRight
} from 'lucide-react';
import { fetchEvalResults, triggerEvalRun } from '../services/api';
import type { EvalResults } from '../types';

interface DemoPageProps {
  setActiveTab: (tab: string) => void;
}

export const DemoPage: React.FC<DemoPageProps> = ({ setActiveTab }) => {
  const [evalResults, setEvalResults] = useState<EvalResults | null>(null);
  const [runningEval, setRunningEval] = useState(false);
  const [evalError, setEvalError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState<number>(1);

  const loadEval = async () => {
    try {
      const data = await fetchEvalResults();
      if (data && data.evaluated_deals_count) {
        setEvalResults(data);
      } else {
        setEvalResults(null);
      }
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadEval();
  }, []);

  const handleRunEval = async () => {
    setRunningEval(true);
    setEvalError(null);
    try {
      const res = await triggerEvalRun();
      if (res && res.summary) {
        setEvalResults(res.summary);
      } else {
        await loadEval();
      }
    } catch (err: any) {
      setEvalError(err.message || 'Evaluation run failed');
    } finally {
      setRunningEval(false);
    }
  };

  const steps = [
    {
      num: 1,
      title: 'Analyze Without Hindsight (OFF Baseline)',
      desc: 'Shows generic SaaS procurement recommendations with 0 historical evidence and generic target price.',
      action: () => setActiveTab('negotiation')
    },
    {
      num: 2,
      title: 'Analyze With Hindsight (ON Memory)',
      desc: 'Hindsight recalls past vendor quotes and cross-vendor patterns, citing exact memory IDs and empirical success rates.',
      action: () => setActiveTab('negotiation')
    },
    {
      num: 3,
      title: 'Record Outcome & Retain Memory',
      desc: 'Closing the loop: Retain final negotiated prices, vendor responses, and lessons into Hindsight Cloud.',
      action: () => setActiveTab('outcome')
    },
    {
      num: 4,
      title: 'Immediate Recall Verification',
      desc: 'Subsequent briefings automatically recall the newly retained experience, changing tactical guidance.',
      action: () => setActiveTab('memory')
    },
    {
      num: 5,
      title: 'Sequential Evaluation & Learning Curve',
      desc: '4 held-out deals evaluated sequentially to measure target-price error and tactical hit rates.',
      action: () => {}
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-slate-800 pb-5">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 text-sky-400 text-xs font-mono border border-sky-500/20 mb-2">
          <PlayCircle className="w-3.5 h-3.5" />
          <span>Interactive End-to-End Walkthrough</span>
        </div>
        <h2 className="text-xl font-bold text-white tracking-tight">
          Guided 60–120s Demo & Empirical Evaluation
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Observe how persistent agent memory drives continuous strategic improvement across sequential SaaS deals.
        </p>
      </div>

      {/* Guided 5-Step Progress Flow */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        <h3 className="text-sm font-semibold text-white">DealMemory 5-Step Learning Lifecycle</h3>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
          {steps.map((s) => (
            <div
              key={s.num}
              onClick={() => {
                setActiveStep(s.num);
                if (s.num !== 5) s.action();
              }}
              className={`p-3.5 rounded-lg border cursor-pointer transition flex flex-col justify-between ${
                activeStep === s.num
                  ? 'bg-sky-950/40 border-sky-500 text-sky-200 ring-1 ring-sky-500/30'
                  : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-200 flex items-center justify-center font-bold text-[11px]">
                    {s.num}
                  </span>
                  {activeStep > s.num && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                </div>
                <div className="font-semibold text-white text-[11px] mb-1">{s.title}</div>
                <p className="text-[10px] text-slate-400 leading-normal">{s.desc}</p>
              </div>

              {s.num !== 5 && (
                <div className="mt-3 text-[10px] text-sky-400 font-medium flex items-center gap-1">
                  <span>Go to Step</span>
                  <ChevronRight className="w-3 h-3" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Evaluation Results Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white">Held-Out Evaluation & Learning Curve</h3>
              <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                Sequential Isolation
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              4 held-out deals evaluated in strict chronological date order (OFF vs ON)
            </p>
          </div>

          <button
            onClick={handleRunEval}
            disabled={runningEval}
            className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-white font-medium text-xs transition shadow-sm flex items-center gap-1.5 self-start sm:self-auto disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${runningEval ? 'animate-spin' : ''}`} />
            <span>{runningEval ? 'Evaluating Sequentially...' : 'Run Sequential Evaluation (4 Deals)'}</span>
          </button>
        </div>

        {evalError && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            Evaluation Error: {evalError}
          </div>
        )}

        {!evalResults ? (
          <div className="text-center py-10 text-xs text-slate-500 space-y-3">
            <p>Evaluation has not yet been executed for this session.</p>
            <p>Click "Run Sequential Evaluation" above to evaluate all 4 held-out deals and generate the learning curve.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Aggregate Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {/* Metric 1: Target Price Error */}
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                <span className="text-slate-400">Mean Target-Price Error</span>
                <div className="mt-2 flex items-baseline gap-3">
                  <div>
                    <span className="text-[10px] text-slate-500 block">Memory OFF</span>
                    <span className="text-base font-bold font-mono text-slate-400">
                      {(evalResults.overall_metrics.mean_target_price_error.off_mode * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="text-slate-600">→</div>
                  <div>
                    <span className="text-[10px] text-sky-400 block font-medium">Memory ON</span>
                    <span className="text-base font-bold font-mono text-emerald-400">
                      {(evalResults.overall_metrics.mean_target_price_error.on_mode * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
                <div className="mt-2 text-[11px] text-emerald-400 font-medium">
                  {evalResults.overall_metrics.mean_target_price_error.improvement_factor}
                </div>
              </div>

              {/* Metric 2: Winning Tactic Top-3 Hit Rate */}
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                <span className="text-slate-400">Winning Tactic Top-3 Hit Rate</span>
                <div className="mt-2 flex items-baseline gap-3">
                  <div>
                    <span className="text-[10px] text-slate-500 block">Memory OFF</span>
                    <span className="text-base font-bold font-mono text-slate-400">
                      {evalResults.overall_metrics.winning_tactic_top3_hit_rate.off_mode}
                    </span>
                  </div>
                  <div className="text-slate-600">→</div>
                  <div>
                    <span className="text-[10px] text-sky-400 block font-medium">Memory ON</span>
                    <span className="text-base font-bold font-mono text-emerald-400">
                      {evalResults.overall_metrics.winning_tactic_top3_hit_rate.on_mode}
                    </span>
                  </div>
                </div>
                <div className="mt-2 text-[11px] text-slate-400">
                  Winning tactic correctly prioritized in top-3 recommendations
                </div>
              </div>

              {/* Metric 3: Avoided Mistake Rate */}
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                <span className="text-slate-400">Avoided Known Mistake Rate</span>
                <div className="mt-2 flex items-baseline gap-3">
                  <div>
                    <span className="text-[10px] text-slate-500 block">Memory OFF</span>
                    <span className="text-base font-bold font-mono text-slate-400">
                      {evalResults.overall_metrics.avoided_mistake_rate.off_mode}
                    </span>
                  </div>
                  <div className="text-slate-600">→</div>
                  <div>
                    <span className="text-[10px] text-sky-400 block font-medium">Memory ON</span>
                    <span className="text-base font-bold font-mono text-emerald-400">
                      {evalResults.overall_metrics.avoided_mistake_rate.on_mode}
                    </span>
                  </div>
                </div>
                <div className="mt-2 text-[11px] text-slate-400">
                  Explicitly avoids known failed tactics (e.g. early renewals)
                </div>
              </div>
            </div>

            {/* Learning Curve Table / Visual */}
            <div>
              <div className="flex items-center justify-between mb-2 text-xs">
                <span className="font-semibold text-slate-200">
                  Learning Curve (Experience Bank Growth vs Target-Price Error):
                </span>
                <span className="text-slate-500">Chronological Accretion</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs bg-slate-950/60 border border-slate-800 rounded-lg">
                  <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">Deal ID / Vendor</th>
                      <th className="py-2.5 px-3">Date Anchor</th>
                      <th className="py-2.5 px-3">Experience Count (N)</th>
                      <th className="py-2.5 px-3">OFF Price Error</th>
                      <th className="py-2.5 px-3">ON Price Error</th>
                      <th className="py-2.5 px-3">Error Reduction</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {evalResults.learning_curve.map((pt, idx) => {
                      const dealDetail = evalResults.deal_evaluations[idx];
                      return (
                        <tr key={pt.deal_id} className="hover:bg-slate-800/30 transition">
                          <td className="py-2.5 px-3 font-medium text-white">
                            <div>{pt.deal_id}</div>
                            <div className="text-[11px] text-slate-400">{dealDetail?.vendor || 'Vendor'}</div>
                          </td>
                          <td className="py-2.5 px-3 text-slate-400">{dealDetail?.date || 'N/A'}</td>
                          <td className="py-2.5 px-3 font-mono text-sky-400 font-semibold">
                            {pt.experience_count} deals
                          </td>
                          <td className="py-2.5 px-3 font-mono text-slate-400">
                            {(pt.off_target_price_error * 100).toFixed(1)}%
                          </td>
                          <td className="py-2.5 px-3 font-mono text-emerald-400 font-bold">
                            {(pt.on_target_price_error * 100).toFixed(1)}%
                          </td>
                          <td className="py-2.5 px-3 font-mono text-emerald-400">
                            +{pt.error_reduction_pct}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pattern Cross-Check Audit Flagging */}
            <div>
              <div className="flex items-center justify-between mb-2 text-xs">
                <span className="font-semibold text-slate-200">
                  Audit: LLM Pattern Claims vs SQLite Ground Truth Cross-Check
                </span>
                <span className="text-[10px] text-slate-500 font-mono">Non-Negotiable Verification</span>
              </div>

              <div className="space-y-2 text-xs">
                {evalResults.deal_evaluations.map((deal) => (
                  <div key={deal.deal_id} className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1.5">
                    <div className="font-medium text-white flex items-center justify-between">
                      <span>{deal.deal_id} ({deal.vendor} - {deal.category})</span>
                      <span className="text-slate-400 text-[11px]">Actual Price: ₹{deal.actual_final_price.toLocaleString('en-IN')}</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 text-[11px]">
                      {deal.pattern_cross_checks && deal.pattern_cross_checks.map((pcc: any, pidx: number) => (
                        <div
                          key={pidx}
                          className={`p-2 rounded border ${
                            pcc.mismatch_flagged
                              ? 'bg-amber-950/20 border-amber-500/40 text-amber-300'
                              : 'bg-slate-900 border-slate-800 text-slate-300'
                          }`}
                        >
                          <div className="font-semibold">{pcc.tactic}</div>
                          <div className="mt-0.5 text-[10px]">
                            LLM Reported: {pcc.llm_reported?.successes}/{pcc.llm_reported?.attempts} (
                            {pcc.llm_reported?.rate}%)
                          </div>
                          {pcc.mismatch_flagged && (
                            <div className="mt-1 text-[10px] font-bold text-amber-400">
                              [Flagged Mismatch] Ground Truth had different count. Never silently corrected.
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Mandatory Synthetic Label */}
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-center text-xs text-slate-400">
              <span className="font-semibold text-slate-300">{evalResults.evaluation_label}</span>
              <div className="mt-0.5 text-[11px] text-slate-500">{evalResults.disclaimer}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
