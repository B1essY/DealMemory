import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  ArrowRight,
  ShieldAlert,
  AlertCircle,
  FileText
} from 'lucide-react';
import { createNegotiation, analyzeDeal } from '../services/api';
import type { Negotiation, BriefingResult } from '../types';

interface NegotiationPageProps {
  selectedDeal: Negotiation | null;
  onDealAnalyzed?: (deal: Negotiation) => void;
  onNavigateToOutcome?: (deal: Negotiation) => void;
}

export const NegotiationPage: React.FC<NegotiationPageProps> = ({
  selectedDeal,
  onDealAnalyzed,
  onNavigateToOutcome
}) => {
  // Form State
  const [vendor, setVendor] = useState(selectedDeal?.vendor || 'KavachSec');
  const [product, setProduct] = useState(selectedDeal?.product || 'Kavach Endpoint Shield Enterprise');
  const [category, setCategory] = useState(selectedDeal?.category || 'Cybersecurity');
  const [seats, setSeats] = useState<number>(selectedDeal?.seats || 100);
  const [initialQuote, setInitialQuote] = useState<number>(selectedDeal?.initial_quote || 1500000);
  const [contractDurationMonths, setContractDurationMonths] = useState<number>(
    selectedDeal?.contract_duration_months || 12
  );
  const [supportFee, setSupportFee] = useState<number>(selectedDeal?.support_fee || 300000);
  const [renewalType, setRenewalType] = useState<string>(selectedDeal?.renewal_type || 'Renewal');
  const [deadline, setDeadline] = useState<string>(selectedDeal?.deadline || '2026-10-15');
  const [clauses, setClauses] = useState<string>(
    selectedDeal?.clauses_raised?.join(', ') ||
      'Mandatory premium support tier SLA, 60-day auto-renewal clause, CPI annual price increase'
  );
  const [notes, setNotes] = useState<string>(
    selectedDeal?.notes || 'Vendor quoted a 20% support fee surcharge and proposed standard 60-day auto-renewal.'
  );

  // Active Deal reference
  const [currentDeal, setCurrentDeal] = useState<Negotiation | null>(selectedDeal);

  // Analysis State
  const [offBriefing, setOffBriefing] = useState<BriefingResult | null>(null);
  const [onBriefing, setOnBriefing] = useState<BriefingResult | null>(null);
  const [analyzingOff, setAnalyzingOff] = useState(false);
  const [analyzingOn, setAnalyzingOn] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Update form if selectedDeal changes
  useEffect(() => {
    if (selectedDeal) {
      setCurrentDeal(selectedDeal);
      setVendor(selectedDeal.vendor);
      setProduct(selectedDeal.product);
      setCategory(selectedDeal.category);
      setSeats(selectedDeal.seats);
      setInitialQuote(selectedDeal.initial_quote);
      setContractDurationMonths(selectedDeal.contract_duration_months);
      setSupportFee(selectedDeal.support_fee);
      setRenewalType(selectedDeal.renewal_type);
      setDeadline(selectedDeal.deadline);
      setClauses(selectedDeal.clauses_raised?.join(', ') || '');
      setNotes(selectedDeal.notes || '');
    }
  }, [selectedDeal]);

  // Demo deal prefill
  const fillDemoDeal = () => {
    setVendor('KavachSec');
    setProduct('Kavach Cloud SASE & Threat Shield');
    setCategory('Cybersecurity');
    setSeats(100);
    setInitialQuote(1500000);
    setContractDurationMonths(12);
    setSupportFee(300000);
    setRenewalType('Renewal');
    setDeadline('2026-10-25');
    setClauses('20% platform support fee unbundling, 60-day auto-renewal clause, dedicated TAM SLA');
    setNotes('Demo deal: 100 seats, INR 15L initial quote, INR 3L support fee, auto-renewal on.');
    setCurrentDeal(null);
    setOffBriefing(null);
    setOnBriefing(null);
  };

  const getOrCreateDeal = async (): Promise<Negotiation> => {
    if (currentDeal) return currentDeal;

    const clauseList = clauses
      .split(',')
      .map((c) => c.trim())
      .filter((c) => c.length > 0);

    const newDeal = await createNegotiation({
      vendor,
      product,
      category,
      seats: Number(seats),
      initial_quote: Number(initialQuote),
      contract_duration_months: Number(contractDurationMonths),
      support_fee: Number(supportFee),
      renewal_type: renewalType,
      deadline,
      clauses_raised: clauseList,
      notes
    });

    setCurrentDeal(newDeal);
    if (onDealAnalyzed) onDealAnalyzed(newDeal);
    return newDeal;
  };

  const handleAnalyzeOff = async () => {
    setAnalyzingOff(true);
    setErrorMsg(null);
    try {
      const deal = await getOrCreateDeal();
      const res = await analyzeDeal(deal.id, false);
      setOffBriefing(res);
    } catch (err: any) {
      setErrorMsg(`Analysis (OFF) failed: ${err.message}`);
    } finally {
      setAnalyzingOff(false);
    }
  };

  const handleAnalyzeOn = async () => {
    setAnalyzingOn(true);
    setErrorMsg(null);
    try {
      const deal = await getOrCreateDeal();
      const res = await analyzeDeal(deal.id, true);
      setOnBriefing(res);
    } catch (err: any) {
      setErrorMsg(`Analysis (ON) failed: ${err.message}`);
    } finally {
      setAnalyzingOn(false);
    }
  };

  const handleAnalyzeBoth = async () => {
    await handleAnalyzeOff();
    await handleAnalyzeOn();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">SaaS Negotiation Analysis</h2>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Compare baseline generic market guidance against Hindsight evidence-grounded intelligence.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={fillDemoDeal}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 text-xs font-medium transition"
          >
            Fill Demo Deal (INR 15L)
          </button>
          {currentDeal && onNavigateToOutcome && (
            <button
              onClick={() => onNavigateToOutcome(currentDeal)}
              className="px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-medium transition flex items-center gap-1.5"
            >
              <span>Record Outcome</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Negotiation Parameters Input Form */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <FileText className="w-4 h-4 text-sky-400" />
          <span>Current Deal Parameters</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          {/* Vendor */}
          <div>
            <label className="block text-slate-400 mb-1">Vendor Name</label>
            <select
              value={vendor}
              onChange={(e) => setVendor(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
            >
              <option value="KavachSec">KavachSec (Cybersecurity)</option>
              <option value="VyaparPulse">VyaparPulse (CRM)</option>
              <option value="MeghMonitor">MeghMonitor (Cloud Monitoring)</option>
              <option value="KarmicHR">KarmicHR (HR Software)</option>
              <option value="SetuConnect">SetuConnect (Collaboration)</option>
            </select>
          </div>

          {/* Product */}
          <div>
            <label className="block text-slate-400 mb-1">Product Name</label>
            <input
              type="text"
              value={product}
              onChange={(e) => setProduct(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-slate-400 mb-1">Category</label>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Seats */}
          <div>
            <label className="block text-slate-400 mb-1">Seats / Nodes</label>
            <input
              type="number"
              value={seats}
              onChange={(e) => setSeats(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Initial Quote */}
          <div>
            <label className="block text-slate-400 mb-1">Initial Quote (INR ₹)</label>
            <input
              type="number"
              value={initialQuote}
              onChange={(e) => setInitialQuote(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 font-mono focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Support Fee */}
          <div>
            <label className="block text-slate-400 mb-1">Quoted Support Fee (INR ₹)</label>
            <input
              type="number"
              value={supportFee}
              onChange={(e) => setSupportFee(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 font-mono focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Contract Duration */}
          <div>
            <label className="block text-slate-400 mb-1">Duration (Months)</label>
            <input
              type="number"
              value={contractDurationMonths}
              onChange={(e) => setContractDurationMonths(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Deadline */}
          <div>
            <label className="block text-slate-400 mb-1">Decision Deadline</label>
            <input
              type="date"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Clauses Raised */}
          <div className="sm:col-span-2">
            <label className="block text-slate-400 mb-1">Clauses & Terms Under Discussion</label>
            <input
              type="text"
              value={clauses}
              onChange={(e) => setClauses(e.target.value)}
              placeholder="Comma separated clauses"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Notes */}
          <div className="sm:col-span-2">
            <label className="block text-slate-400 mb-1">Procurement Context & Notes</label>
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any vendor context or special circumstances"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-5 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs text-slate-400">
            {currentDeal ? (
              <span className="text-sky-400">Deal Registered: ID {currentDeal.id}</span>
            ) : (
              <span>Deal will be created automatically on analysis.</span>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={handleAnalyzeOff}
              disabled={analyzingOff}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium text-xs border border-slate-700 transition"
            >
              {analyzingOff ? 'Analyzing...' : '1. Analyze Without Hindsight (OFF Baseline)'}
            </button>
            <button
              onClick={handleAnalyzeOn}
              disabled={analyzingOn}
              className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-white font-medium text-xs transition shadow-sm flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{analyzingOn ? 'Recalling & Briefing...' : '2. Analyze With Hindsight (ON Memory)'}</span>
            </button>
            <button
              onClick={handleAnalyzeBoth}
              disabled={analyzingOff || analyzingOn}
              className="px-3 py-2 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-400 text-xs border border-slate-800 transition"
            >
              Run Both Side-by-Side
            </button>
          </div>
        </div>
      </div>

      {/* Side-by-Side Comparison Container */}
      {(offBriefing || onBriefing) && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <span>Negotiation Strategy Briefings</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 font-normal">
                Side-by-Side Evaluation
              </span>
            </h3>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* ----------------- LEFT: MEMORY OFF (BASELINE) ----------------- */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-slate-600"></div>
                  <span className="text-sm font-bold text-slate-200">Baseline (Memory OFF)</span>
                </div>
                <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                  Generic Best Practices
                </span>
              </div>

              {!offBriefing ? (
                <div className="text-center py-12 text-xs text-slate-500">
                  Click "Analyze Without Hindsight" to view baseline guidance.
                </div>
              ) : (
                <div className="space-y-4 text-xs">
                  {/* Target & Walk-away Prices */}
                  <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-950/80 border border-slate-800">
                    <div>
                      <span className="text-[11px] text-slate-400">Target Counter-Offer</span>
                      <div className="text-lg font-bold font-mono text-slate-200 mt-0.5">
                        ₹{offBriefing.briefing.target_price.toLocaleString('en-IN')}
                      </div>
                      <div className="text-[10px] text-slate-500 mt-1">
                        {offBriefing.briefing.target_price_reasoning}
                      </div>
                    </div>
                    <div>
                      <span className="text-[11px] text-slate-400">Walk-Away Ceiling</span>
                      <div className="text-lg font-bold font-mono text-slate-400 mt-0.5">
                        ₹{offBriefing.briefing.walk_away_price.toLocaleString('en-IN')}
                      </div>
                      <div className="text-[10px] text-slate-500 mt-1">
                        {offBriefing.briefing.walk_away_price_reasoning}
                      </div>
                    </div>
                  </div>

                  {/* Historical Evidence Check */}
                  <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-slate-500">
                    <span className="font-semibold text-slate-400 block mb-1">Historical Evidence (From Memory):</span>
                    <p className="italic">
                      {offBriefing.briefing.historical_evidence.length === 0
                        ? 'No historical evidence (Memory OFF). Uses generic SaaS market knowledge only.'
                        : offBriefing.briefing.historical_evidence[0]?.claim}
                    </p>
                  </div>

                  {/* Recommended Tactics */}
                  <div>
                    <span className="font-semibold text-slate-300 block mb-2">Recommended General Tactics:</span>
                    <div className="space-y-2">
                      {offBriefing.briefing.recommended_tactics.map((t) => (
                        <div key={t.rank} className="p-2.5 rounded bg-slate-950 border border-slate-800">
                          <div className="font-medium text-slate-200">
                            [{t.rank}] {t.tactic}
                          </div>
                          <div className="text-slate-400 mt-0.5">{t.reason}</div>
                          <div className="text-[10px] text-slate-500 mt-1 italic">
                            Grounding: {t.supporting_evidence}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Tactics to Avoid */}
                  {offBriefing.briefing.tactics_to_avoid.length > 0 && (
                    <div>
                      <span className="font-semibold text-slate-400 block mb-1">General Avoidances:</span>
                      <ul className="list-disc list-inside text-slate-400 space-y-0.5">
                        {offBriefing.briefing.tactics_to_avoid.map((a, i) => (
                          <li key={i}>{a}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* ----------------- RIGHT: MEMORY ON (HINDSIGHT GROUNDED) ----------------- */}
            <div className="bg-slate-900 border border-sky-500/40 rounded-xl p-5 space-y-4 shadow-lg shadow-sky-950/20 ring-1 ring-sky-500/20">
              <div className="flex items-center justify-between border-b border-sky-500/20 pb-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-sky-400 animate-pulse" />
                  <span className="text-sm font-bold text-sky-400">DealMemory (Memory ON)</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] px-2 py-0.5 rounded bg-sky-500/10 text-sky-300 border border-sky-500/30 font-mono">
                    {onBriefing?.recall_stats?.total_unique_memories || 0} Recalled Facts
                  </span>
                  <span className="text-[11px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-medium">
                    Evidence Grounded
                  </span>
                </div>
              </div>

              {!onBriefing ? (
                <div className="text-center py-12 text-xs text-slate-500">
                  Click "Analyze With Hindsight" to retrieve memory and generate briefing.
                </div>
              ) : (
                <div className="space-y-4 text-xs">
                  {/* Target & Walk-away Prices with Reasoning */}
                  <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-slate-950 border border-sky-500/30">
                    <div>
                      <span className="text-[11px] text-sky-300 font-medium">Target Counter-Offer</span>
                      <div className="text-lg font-bold font-mono text-emerald-400 mt-0.5">
                        ₹{onBriefing.briefing.target_price.toLocaleString('en-IN')}
                      </div>
                      <div className="text-[10px] text-slate-300 mt-1">
                        {onBriefing.briefing.target_price_reasoning}
                      </div>
                    </div>
                    <div>
                      <span className="text-[11px] text-slate-400 font-medium">Walk-Away Ceiling</span>
                      <div className="text-lg font-bold font-mono text-slate-200 mt-0.5">
                        ₹{onBriefing.briefing.walk_away_price.toLocaleString('en-IN')}
                      </div>
                      <div className="text-[10px] text-slate-400 mt-1">
                        {onBriefing.briefing.walk_away_price_reasoning}
                      </div>
                    </div>
                  </div>

                  {/* Historical Evidence with Citations (Strict Non-Negotiable) */}
                  <div className="p-3 rounded-lg bg-sky-950/30 border border-sky-500/20">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-sky-300">
                        Historical Evidence ({onBriefing.briefing.historical_evidence.length} claims cited):
                      </span>
                      <span className="text-[10px] text-slate-400">Strict Hindsight Citations</span>
                    </div>

                    {onBriefing.briefing.historical_evidence.length === 0 ? (
                      <p className="italic text-slate-400">No relevant organizational experience found.</p>
                    ) : (
                      <div className="space-y-2">
                        {onBriefing.briefing.historical_evidence.map((ev, i) => (
                          <div key={i} className="p-2 rounded bg-slate-950/80 border border-sky-500/20">
                            <div className="font-medium text-slate-200">{ev.claim}</div>
                            <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400">
                              <span className="font-mono text-sky-400">Ref: {ev.supporting_memory_id}</span>
                              <span className="text-slate-500">{ev.relevance}</span>
                            </div>
                            <div className="mt-1 text-[11px] text-slate-300 italic border-l-2 border-sky-500 pl-2">
                              "{ev.source_excerpt_or_reference}"
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Learned Patterns with Empirical Success Rates */}
                  {onBriefing.briefing.learned_patterns.length > 0 && (
                    <div>
                      <span className="font-semibold text-slate-200 block mb-2">
                        Learned Patterns (Derived From Recalled Memories):
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {onBriefing.briefing.learned_patterns.map((p, idx) => (
                          <div key={idx} className="p-2.5 rounded bg-slate-950 border border-slate-800">
                            <div className="flex items-center justify-between">
                              <span className="font-medium text-slate-200 truncate">{p.tactic}</span>
                              <span className="font-mono text-sky-400 font-bold ml-1">
                                {p.success_rate.toFixed(0)}%
                              </span>
                            </div>
                            <div className="text-[10px] text-slate-400 mt-1">
                              {p.successes} wins / {p.attempts} attempts
                            </div>
                            <div className="text-[10px] text-slate-400 mt-0.5">{p.interpretation}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommended Tactics Ranked with Direct Citations */}
                  <div>
                    <span className="font-semibold text-slate-200 block mb-2">
                      Recommended Strategic Tactics:
                    </span>
                    <div className="space-y-2">
                      {onBriefing.briefing.recommended_tactics.map((t) => (
                        <div key={t.rank} className="p-2.5 rounded bg-slate-950 border border-sky-500/20">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-sky-300">
                              [{t.rank}] {t.tactic}
                            </span>
                            <span
                              className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                                t.confidence === 'High'
                                  ? 'bg-emerald-500/20 text-emerald-300'
                                  : 'bg-amber-500/20 text-amber-300'
                              }`}
                            >
                              {t.confidence} Conf.
                            </span>
                          </div>
                          <div className="text-slate-300 mt-1">{t.reason}</div>
                          <div className="text-[10px] text-sky-400/90 mt-1 flex items-start gap-1">
                            <span className="font-semibold">Evidence:</span>
                            <span>{t.supporting_evidence}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Tactics to Avoid (Failure Memory) */}
                  {onBriefing.briefing.tactics_to_avoid.length > 0 && (
                    <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-500/30">
                      <div className="flex items-center gap-1.5 font-semibold text-rose-300 mb-1">
                        <ShieldAlert className="w-3.5 h-3.5" />
                        <span>Tactics to Avoid (Failure Memory Active):</span>
                      </div>
                      <ul className="list-disc list-inside text-rose-200/90 space-y-0.5">
                        {onBriefing.briefing.tactics_to_avoid.map((a, i) => (
                          <li key={i}>{a}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Temporal Observations */}
                  {onBriefing.briefing.temporal_observations.length > 0 && (
                    <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
                      <span className="font-semibold text-amber-400 block mb-1">Temporal Pattern:</span>
                      <ul className="list-disc list-inside space-y-0.5">
                        {onBriefing.briefing.temporal_observations.map((to, i) => (
                          <li key={i}>{to}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
