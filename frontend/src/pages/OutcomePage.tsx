import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  AlertCircle,
  Plus,
  Trash2,
  Sparkles,
  Building2
} from 'lucide-react';
import { fetchNegotiations, recordOutcome } from '../services/api';
import type { Negotiation, Outcome, TacticAttempt } from '../types';

interface OutcomePageProps {
  deal: Negotiation | null;
  onOutcomeSaved?: (outcome: Outcome) => void;
  setActiveTab?: (tab: string) => void;
}

export const OutcomePage: React.FC<OutcomePageProps> = ({
  deal: initialDeal,
  onOutcomeSaved,
  setActiveTab
}) => {
  const [deals, setDeals] = useState<Negotiation[]>([]);
  const [selectedDealId, setSelectedDealId] = useState<string>(initialDeal?.id || '');
  const [currentDeal, setCurrentDeal] = useState<Negotiation | null>(initialDeal);

  // Outcome Form State
  const [finalPrice, setFinalPrice] = useState<number>(1240000);
  const [contractDurationMonths, setContractDurationMonths] = useState<number>(12);
  const [vendorResponse, setVendorResponse] = useState<string>(
    'Vendor was firm on standard 20% support fee until line-item SLA challenge. Waived premium SLA and dropped support.'
  );
  const [termsAcceptedRejected, setTermsAcceptedRejected] = useState<string>(
    'Accepted standard 4-hour SLA tier; refused paid dedicated technical account manager add-on.'
  );
  const [lessonsLearned, setLessonsLearned] = useState<string>(
    'Support-fee unbundling challenge succeeded again on KavachSec, delivering 18% support savings. Multi-year lock-in was refused.'
  );
  const [notes] = useState<string>(
    'Settled within target price threshold. Deal finalized on schedule.'
  );

  // Tactics attempted list
  const [tactics, setTactics] = useState<TacticAttempt[]>([
    {
      tactic: 'Support-fee unbundling challenge',
      vendor_response: 'Agreed to reduce support fee from INR 3,00,000 to INR 2,46,000 (18% reduction)',
      success: true
    },
    {
      tactic: 'Multi-year commitment trade',
      vendor_response: 'Refused multi-year pricing discounts citing cybersecurity volatility',
      success: false
    }
  ]);

  const [saving, setSaving] = useState(false);
  const [savedOutcome, setSavedOutcome] = useState<Outcome | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchNegotiations()
      .then((data) => {
        setDeals(data);
        if (!selectedDealId && data.length > 0) {
          setSelectedDealId(data[0].id);
          setCurrentDeal(data[0]);
        }
      })
      .catch((err) => console.error(err));
  }, []);

  const handleSelectDeal = (id: string) => {
    setSelectedDealId(id);
    const found = deals.find((d) => d.id === id) || null;
    setCurrentDeal(found);
    if (found) {
      setFinalPrice(Math.round(found.initial_quote * 0.83));
      setContractDurationMonths(found.contract_duration_months || 12);
    }
  };

  const handleAddTactic = () => {
    setTactics([
      ...tactics,
      {
        tactic: 'Competitor alternative leverage',
        vendor_response: 'Vendor matched competitor tier pricing',
        success: true
      }
    ]);
  };

  const handleRemoveTactic = (idx: number) => {
    setTactics(tactics.filter((_, i) => i !== idx));
  };

  const handleUpdateTactic = (idx: number, field: keyof TacticAttempt, value: any) => {
    const updated = [...tactics];
    updated[idx] = { ...updated[idx], [field]: value };
    setTactics(updated);
  };

  const handleSaveToHindsight = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDealId) {
      setErrorMessage('Please select a negotiation deal to record an outcome.');
      return;
    }

    setSaving(true);
    setErrorMessage(null);
    setSavedOutcome(null);

    const successfulTactics = tactics.filter((t) => t.success).map((t) => t.tactic);
    const failedTactics = tactics.filter((t) => !t.success).map((t) => t.tactic);

    try {
      const outcomePayload = {
        final_price: Number(finalPrice),
        contract_duration_months: Number(contractDurationMonths),
        tactics_attempted: tactics,
        vendor_response: vendorResponse,
        successful_tactics: successfulTactics,
        failed_tactics: failedTactics,
        terms_accepted_rejected: termsAcceptedRejected,
        lessons_learned: lessonsLearned,
        notes
      };

      const result = await recordOutcome(selectedDealId, outcomePayload);
      setSavedOutcome(result);
      if (onOutcomeSaved) onOutcomeSaved(result);
    } catch (err: any) {
      setErrorMessage(`Retention failed: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-slate-800 pb-5">
        <h2 className="text-xl font-bold text-white tracking-tight">Record Negotiation Outcome</h2>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Complete the negotiation learning loop: Retain real commercial outcomes into Hindsight Cloud so future briefings improve.
        </p>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-5 h-5 shrink-0 text-rose-400" />
          <div>
            <div className="font-semibold">Retention Failed (Real Error):</div>
            <div>{errorMessage}</div>
          </div>
        </div>
      )}

      {/* Success Notification */}
      {savedOutcome && (
        <div className="p-5 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-200 text-xs space-y-3">
          <div className="flex items-center gap-2 text-sm font-bold text-emerald-300">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <span>DealMemory Learned From This Negotiation!</span>
          </div>
          <p className="text-slate-300">
            The outcome was converted into a structured experience narrative and retained to Hindsight Cloud.
            Recall verification confirmed the memory is searchable for all future briefings.
          </p>

          <div className="p-3 rounded-lg bg-slate-950/80 border border-emerald-500/20 text-slate-300 space-y-1 font-mono text-[11px]">
            <div><span className="text-slate-400">Document ID:</span> {savedOutcome.hindsight_doc_id}</div>
            <div><span className="text-slate-400">Final Price Settled:</span> ₹{savedOutcome.final_price.toLocaleString('en-IN')}</div>
            <div><span className="text-slate-400">Successful Tactics:</span> {savedOutcome.successful_tactics.join(', ') || 'None'}</div>
            <div><span className="text-slate-400">Failed Tactics:</span> {savedOutcome.failed_tactics.join(', ') || 'None'}</div>
            <div><span className="text-slate-400">Key Takeaway:</span> "{savedOutcome.lessons_learned}"</div>
          </div>

          <div className="pt-2 flex items-center gap-3">
            {setActiveTab && (
              <button
                onClick={() => setActiveTab('negotiation')}
                className="px-3 py-1.5 rounded-lg bg-emerald-500 text-white font-medium text-xs hover:bg-emerald-400 transition"
              >
                Start New Negotiation (To Test Recall) →
              </button>
            )}
          </div>
        </div>
      )}

      {/* Form Card */}
      <form onSubmit={handleSaveToHindsight} className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-5">
        {/* Deal Selector */}
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">
            Select Negotiation Deal to Conclude
          </label>
          <select
            value={selectedDealId}
            onChange={(e) => handleSelectDeal(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
          >
            {deals.map((d) => (
              <option key={d.id} value={d.id}>
                {d.vendor} - {d.product} (Quote: ₹{d.initial_quote.toLocaleString('en-IN')} | Seats: {d.seats}) [{d.id}]
              </option>
            ))}
          </select>
        </div>

        {/* Selected Deal Summary Pill */}
        {currentDeal && (
          <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <Building2 className="w-4 h-4 text-sky-400" />
              <span className="font-semibold text-white">{currentDeal.vendor}</span>
              <span className="text-slate-400">{currentDeal.product}</span>
            </div>
            <div className="flex items-center gap-4 text-slate-400">
              <span>Seats: {currentDeal.seats}</span>
              <span>Initial: ₹{currentDeal.initial_quote.toLocaleString('en-IN')}</span>
              <span>Support: ₹{currentDeal.support_fee.toLocaleString('en-IN')}</span>
            </div>
          </div>
        )}

        {/* Financial Outcome */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Final Agreed Contract Price (INR ₹)</label>
            <input
              type="number"
              value={finalPrice}
              onChange={(e) => setFinalPrice(Number(e.target.value))}
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 font-mono focus:outline-none focus:border-sky-500"
            />
            {currentDeal && (
              <div className="text-[11px] text-emerald-400 mt-1">
                Savings: ₹{(currentDeal.initial_quote - finalPrice).toLocaleString('en-IN')} (
                {(((currentDeal.initial_quote - finalPrice) / currentDeal.initial_quote) * 100).toFixed(1)}% reduction)
              </div>
            )}
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Contract Duration Agreed (Months)</label>
            <input
              type="number"
              value={contractDurationMonths}
              onChange={(e) => setContractDurationMonths(Number(e.target.value))}
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        {/* Tactics Attempted & Vendor Responses */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="block text-xs font-semibold text-slate-300">
              Tactics Attempted & Vendor Responses
            </label>
            <button
              type="button"
              onClick={handleAddTactic}
              className="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1 font-medium"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Tactic</span>
            </button>
          </div>

          <div className="space-y-2">
            {tactics.map((t, idx) => (
              <div key={idx} className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 space-y-2 text-xs">
                <div className="flex items-center justify-between gap-3">
                  <input
                    type="text"
                    value={t.tactic}
                    onChange={(e) => handleUpdateTactic(idx, 'tactic', e.target.value)}
                    placeholder="Tactic name"
                    className="w-2/3 bg-slate-900 border border-slate-800 rounded px-2.5 py-1 text-slate-200"
                  />
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => handleUpdateTactic(idx, 'success', !t.success)}
                      className={`px-2 py-1 rounded text-[11px] font-medium transition ${
                        t.success
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      }`}
                    >
                      {t.success ? 'Worked (Success)' : 'Failed / Refused'}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleRemoveTactic(idx)}
                      className="text-slate-500 hover:text-rose-400 p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <input
                  type="text"
                  value={t.vendor_response}
                  onChange={(e) => handleUpdateTactic(idx, 'vendor_response', e.target.value)}
                  placeholder="How did the vendor respond to this tactic?"
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1 text-slate-300 text-xs"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Narrative Qualitative Fields */}
        <div className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-400 mb-1">Overall Vendor Negotiation Behavior</label>
            <textarea
              rows={2}
              value={vendorResponse}
              onChange={(e) => setVendorResponse(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Terms & Clauses Accepted vs Refused</label>
            <input
              type="text"
              value={termsAcceptedRejected}
              onChange={(e) => setTermsAcceptedRejected(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-semibold text-sky-400">
              Key Lesson Learned (Will Be Preserved in Hindsight for Future Deals)
            </label>
            <textarea
              rows={2}
              value={lessonsLearned}
              onChange={(e) => setLessonsLearned(e.target.value)}
              className="w-full bg-slate-950 border border-sky-500/30 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        {/* Submit */}
        <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Retains into bank: <code className="text-slate-400 font-mono">dealmemory-org-prod</code>
          </span>
          <button
            type="submit"
            disabled={saving}
            className="px-5 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-white font-semibold text-xs transition shadow-sm flex items-center gap-2 disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            <span>{saving ? 'Retaining & Verifying Memory...' : 'Save to Hindsight'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
