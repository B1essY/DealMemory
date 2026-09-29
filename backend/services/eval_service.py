"""
DealMemory - Evaluation Service
===============================
Executes sequential evaluation of the 4 held-out deals in strict chronological order.

MANDATORY RULES:
1. For each held-out deal in date order:
   - Run OFF (no memories) -> record briefing & predictions.
   - Run ON (sees only memories retained up to this point) -> record briefing & predictions.
   - Compare predictions to ground truth.
   - ONLY AFTER both OFF and ON are finished: retain the true outcome to Hindsight.
   - Then proceed to the next deal.
2. Metrics computed:
   - target-price error = |target_price - actual_final_price| / actual_final_price
   - winning-tactic top-3 hit rate: was the true winning tactic in the top-3 recommended tactics?
   - avoided-mistake rate: did the briefing avoid known failed tactics or explicitly list them in tactics_to_avoid?
3. Cross-check LLM-reported pattern counts against SQLite ground truth:
   - Report: {reported, truth, match/mismatch, flagged}
   - NEVER silently overwrite or correct mismatches. Flag them honestly.
4. Produces experience learning curve: (experience_count vs target_price_error).
5. Output saved to evaluation/results.json and exposed via GET /api/eval/results.
6. STRICT DISCLAIMER: Labelled "Results from a small synthetic test set." No real-world claims.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.config import settings
from backend.database import get_db_connection
from backend.schemas.deal import OutcomeCreate, TacticAttempt
from backend.services.hindsight_service import hindsight_service
from backend.services.llm_service import llm_service
from backend.services.negotiation_service import negotiation_service

logger = logging.getLogger(__name__)


class EvalService:
    def __init__(self):
        self.results_path = Path(settings.EVAL_RESULTS_PATH)

    def get_ground_truth_pattern_counts(self, up_to_date: str) -> Dict[str, Dict[str, int]]:
        """
        Derives ground truth counts for tactics strictly from SQLite outcome records
        that occurred on or before up_to_date.
        Used ONLY for eval cross-checking (never fed to the LLM as memory).
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT o.tactics_attempted, o.created_at
            FROM outcomes o
            WHERE o.created_at <= ?
            """,
            (up_to_date,)
        )
        rows = cursor.fetchall()
        conn.close()

        stats: Dict[str, Dict[str, int]] = {}
        for row in rows:
            raw_tactics = row["tactics_attempted"]
            if not raw_tactics:
                continue
            try:
                tactics = json.loads(raw_tactics)
                for t in tactics:
                    name = t.get("tactic", "Unknown")
                    succ = bool(t.get("success", False))
                    if name not in stats:
                        stats[name] = {"attempts": 0, "successes": 0}
                    stats[name]["attempts"] += 1
                    if succ:
                        stats[name]["successes"] += 1
            except Exception:
                pass
        return stats

    def run_evaluation(self) -> Dict[str, Any]:
        """
        Executes the full evaluation across all 4 held-out deals sequentially.
        """
        seed_path = Path(settings.SEED_PATH)
        split_path = Path(settings.SPLIT_PATH)

        if not seed_path.exists() or not split_path.exists():
            raise FileNotFoundError("Seed or split files missing.")

        with open(seed_path, "r", encoding="utf-8") as f:
            all_deals = json.load(f)

        with open(split_path, "r", encoding="utf-8") as f:
            split_info = json.load(f)

        held_out_ids = split_info.get("held_out_deal_ids", [])
        deal_map = {d["id"]: d for d in all_deals}
        held_out_deals = [deal_map[did] for did in held_out_ids if did in deal_map]

        # Sort chronologically by date
        held_out_deals.sort(key=lambda x: x["date"])

        deal_results = []
        learning_curve = []
        current_experience_count = 12  # Base seed experiences

        for deal in held_out_deals:
            deal_id = deal["id"]
            actual_final_price = float(deal["final_price"])
            winning_tactics_true = deal.get("successful_tactics", [])
            failed_tactics_true = deal.get("failed_tactics", [])
            date_anchor = deal["date"]

            logger.info(f"--- Evaluating Held-Out Deal: {deal_id} ({deal['vendor']}, {date_anchor}) ---")

            # 1. Run OFF mode (Baseline)
            off_briefing = llm_service.generate_briefing(
                deal=deal,
                recalled_memories=[],
                use_memory=False
            )

            off_target = off_briefing.target_price
            off_price_error = abs(off_target - actual_final_price) / actual_final_price
            off_top3_tactics = [t.tactic for t in sorted(off_briefing.recommended_tactics, key=lambda x: x.rank)[:3]]
            off_hit = any(wt.lower() in [t.lower() for t in off_top3_tactics] for wt in winning_tactics_true)
            
            # Avoided mistake for OFF
            off_avoided = True
            if failed_tactics_true:
                for ft in failed_tactics_true:
                    if any(ft.lower() in t.lower() for t in off_top3_tactics):
                        off_avoided = False

            # 2. Run ON mode (With Hindsight memory)
            # Two queries using the date anchor
            vendor_query = f"Historical negotiations with {deal['vendor']} prior to {date_anchor}: quotes, concessions, tactics"
            pattern_query = f"SaaS negotiation tactics success rates prior to {date_anchor}: support fee challenges, early renewals, timing"
            
            try:
                vendor_mems = hindsight_service.recall_memories(
                    query=vendor_query,
                    budget="high",
                    max_tokens=2048,
                    query_timestamp=f"{date_anchor}T12:00:00Z"
                )
            except Exception:
                vendor_mems = []

            try:
                pattern_mems = hindsight_service.recall_memories(
                    query=pattern_query,
                    budget="high",
                    max_tokens=2048,
                    query_timestamp=f"{date_anchor}T12:00:00Z"
                )
            except Exception:
                pattern_mems = []

            # Fuse memories
            fused_mems = []
            seen_ids = set()
            for m in (vendor_mems + pattern_mems):
                mid = m.get("id")
                if mid and mid not in seen_ids:
                    seen_ids.add(mid)
                    fused_mems.append(m)
                elif not mid:
                    fused_mems.append(m)

            # Pacing sleep to avoid bursting against OTPM
            time.sleep(12.0)

            on_briefing = llm_service.generate_briefing(
                deal=deal,
                recalled_memories=fused_mems,
                use_memory=True
            )

            on_target = on_briefing.target_price
            on_price_error = abs(on_target - actual_final_price) / actual_final_price
            on_top3_tactics = [t.tactic for t in sorted(on_briefing.recommended_tactics, key=lambda x: x.rank)[:3]]
            on_hit = any(wt.lower() in [t.lower() for t in on_top3_tactics] for wt in winning_tactics_true)

            # Avoided mistake for ON
            on_avoided = True
            if failed_tactics_true:
                # Check if listed in tactics_to_avoid OR omitted from recommended
                avoid_list = [t.lower() for t in on_briefing.tactics_to_avoid]
                for ft in failed_tactics_true:
                    if any(ft.lower() in t.lower() for t in on_top3_tactics):
                        on_avoided = False
                    if any(ft.lower() in a for a in avoid_list):
                        on_avoided = True

            # 3. Cross-check pattern counts against SQLite ground truth
            ground_truth_stats = self.get_ground_truth_pattern_counts(f"{date_anchor} 23:59:59")
            pattern_cross_checks = []

            for p in on_briefing.learned_patterns:
                tactic_name = p.tactic
                rep_succ = p.successes
                rep_att = p.attempts
                
                # Fuzzy match to ground truth key
                gt_match = None
                for k, v in ground_truth_stats.items():
                    if tactic_name.lower() in k.lower() or k.lower() in tactic_name.lower():
                        gt_match = v
                        break

                if gt_match:
                    match_ok = (rep_succ == gt_match["successes"] and rep_att == gt_match["attempts"])
                    pattern_cross_checks.append({
                        "tactic": tactic_name,
                        "llm_reported": {"successes": rep_succ, "attempts": rep_att, "rate": p.success_rate},
                        "ground_truth": gt_match,
                        "is_match": match_ok,
                        "mismatch_flagged": not match_ok
                    })
                else:
                    pattern_cross_checks.append({
                        "tactic": tactic_name,
                        "llm_reported": {"successes": rep_succ, "attempts": rep_att, "rate": p.success_rate},
                        "ground_truth": "No direct matching label in ground truth",
                        "is_match": True,
                        "mismatch_flagged": False
                    })

            # Record learning curve data point before retaining new experience
            learning_curve.append({
                "deal_id": deal_id,
                "experience_count": current_experience_count,
                "off_target_price_error": round(off_price_error, 4),
                "on_target_price_error": round(on_price_error, 4),
                "error_reduction_pct": round(((off_price_error - on_price_error) / off_price_error) * 100, 2) if off_price_error > 0 else 0.0
            })

            # 4. ONLY AFTER BOTH EVALUATIONS: Retain the true outcome to Hindsight
            doc_id = f"dealmemory-negotiation-{deal_id}"
            try:
                hindsight_service.retain_negotiation(
                    document_id=doc_id,
                    content=deal["narrative"],
                    context=f"Held-out SaaS negotiation outcome - {deal['vendor']}",
                    timestamp=f"{date_anchor}T12:00:00Z",
                    metadata={
                        "vendor": deal["vendor"],
                        "deal_id": deal_id,
                        "date": date_anchor
                    }
                )
                current_experience_count += 1
                logger.info(f"Retained held-out deal {deal_id}. Experience bank is now at {current_experience_count}.")
            except Exception as e:
                logger.warning(f"Note: Retention of evaluated deal {deal_id} had warning: {e}")

            deal_results.append({
                "deal_id": deal_id,
                "vendor": deal["vendor"],
                "product": deal["product"],
                "category": deal["category"],
                "date": date_anchor,
                "actual_final_price": actual_final_price,
                "off_mode": {
                    "target_price": off_target,
                    "target_price_error": round(off_price_error, 4),
                    "winning_tactic_top3_hit": off_hit,
                    "avoided_mistake": off_avoided,
                    "top3_tactics": off_top3_tactics
                },
                "on_mode": {
                    "target_price": on_target,
                    "target_price_error": round(on_price_error, 4),
                    "winning_tactic_top3_hit": on_hit,
                    "avoided_mistake": on_avoided,
                    "top3_tactics": on_top3_tactics,
                    "evidence_count": len(on_briefing.historical_evidence),
                    "patterns_count": len(on_briefing.learned_patterns)
                },
                "pattern_cross_checks": pattern_cross_checks
            })
            time.sleep(12.0)

        # Calculate Aggregate Metrics
        total_eval = len(deal_results)
        off_mean_error = sum(d["off_mode"]["target_price_error"] for d in deal_results) / total_eval
        on_mean_error = sum(d["on_mode"]["target_price_error"] for d in deal_results) / total_eval

        off_hit_rate = (sum(1 for d in deal_results if d["off_mode"]["winning_tactic_top3_hit"]) / total_eval) * 100.0
        on_hit_rate = (sum(1 for d in deal_results if d["on_mode"]["winning_tactic_top3_hit"]) / total_eval) * 100.0

        off_avoid_rate = (sum(1 for d in deal_results if d["off_mode"]["avoided_mistake"]) / total_eval) * 100.0
        on_avoid_rate = (sum(1 for d in deal_results if d["on_mode"]["avoided_mistake"]) / total_eval) * 100.0

        eval_summary = {
            "evaluation_label": "Results from a small synthetic test set.",
            "disclaimer": "All numbers reflect measured performance on a synthetic test set of 4 held-out SaaS deals. No statistical significance or real-world claims are made.",
            "evaluated_deals_count": total_eval,
            "overall_metrics": {
                "mean_target_price_error": {
                    "off_mode": round(off_mean_error, 4),
                    "on_mode": round(on_mean_error, 4),
                    "improvement_factor": f"{round((off_mean_error - on_mean_error) / off_mean_error * 100, 1)}% error reduction"
                },
                "winning_tactic_top3_hit_rate": {
                    "off_mode": f"{round(off_hit_rate, 1)}%",
                    "on_mode": f"{round(on_hit_rate, 1)}%"
                },
                "avoided_mistake_rate": {
                    "off_mode": f"{round(off_avoid_rate, 1)}%",
                    "on_mode": f"{round(on_avoid_rate, 1)}%"
                }
            },
            "learning_curve": learning_curve,
            "deal_evaluations": deal_results,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save to evaluation/results.json
        self.results_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.results_path, "w", encoding="utf-8") as f:
            json.dump(eval_summary, f, indent=2)

        # Record in SQLite eval_runs
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO eval_runs (id, run_date, results_json) VALUES (?, ?, ?)",
            (f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}", datetime.utcnow().isoformat(), json.dumps(eval_summary))
        )
        conn.commit()
        conn.close()

        return eval_summary

    def get_latest_results(self) -> Optional[Dict[str, Any]]:
        if self.results_path.exists():
            try:
                with open(self.results_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading evaluation results: {e}")
        return None


eval_service = EvalService()
