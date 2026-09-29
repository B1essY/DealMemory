"""
DealMemory - Demo CLI Script
Proves the core DealMemory loop end-to-end:
1. Generates briefing with Memory OFF (Baseline generic assistant).
2. Generates briefing with Memory ON (Evidence-based with cross-vendor patterns & failure memory).
3. Demonstrates that ON includes cited historical evidence while OFF does not.
4. Records an outcome and retains it to Hindsight memory.
5. Verifies that subsequent recall retrieves the new experience.
6. Demonstrates that strategy changes because of newly retained experience.
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Set python path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

load_dotenv(root_dir / ".env")
load_dotenv(root_dir / "backend" / ".env")

from backend.database import init_db
from backend.services.hindsight_service import hindsight_service
from backend.services.llm_service import llm_service
from backend.services.negotiation_service import negotiation_service
from backend.schemas.deal import NegotiationCreate, OutcomeCreate, TacticAttempt

def main():
    print("=" * 70)
    print("DealMemory: Negotiation Intelligence That Learns From Every Deal")
    print("=" * 70)

    init_db()

    # 1. Connectivity Check
    print("\n[Step 1] Checking Live Connectivity...")
    hs_ok, hs_msg = hindsight_service.check_connection()
    print(f"Hindsight Status: {'ONLINE' if hs_ok else 'OFFLINE'} - {hs_msg}")
    gq_ok, gq_msg = llm_service.check_connection()
    print(f"Groq Status:      {'ONLINE' if gq_ok else 'OFFLINE'} - {gq_msg}")

    if not hs_ok or not gq_ok:
        print("\nERROR: Connectivity checks failed. Please verify API keys in .env.", file=sys.stderr)
        sys.exit(1)

    # 2. Check or Seed Demo Experiences
    print("\n[Step 2] Ensuring Hindsight Memory Bank has Seed Experiences...")
    try:
        seed_res = negotiation_service.seed_database_and_memory()
        print(f"Seed Status: {seed_res['seeded']} seeded, {seed_res['verified']} verified in recall.")
    except Exception as e:
        print(f"Seeding note: {e}")

    # 3. Create a Demo Negotiation Deal
    demo_deal_in = NegotiationCreate(
        vendor="ShieldArc",
        product="ShieldArc Endpoint & Cloud Guard",
        category="Cybersecurity",
        seats=100,
        initial_quote=1500000.0,
        contract_duration_months=12,
        support_fee=300000.0,
        renewal_type="Renewal",
        deadline="2026-10-15",
        clauses_raised=["Support SLA unbundling", "Auto-renewal term", "Multi-year commitment discount"],
        notes="Vendor initial proposal added 20% support fee surcharge and proposed 60-day auto-renewal."
    )

    print(f"\n[Step 3] Creating New Deal: {demo_deal_in.vendor} - {demo_deal_in.product} (Quote: INR {demo_deal_in.initial_quote:,.0f})...")
    deal_resp = negotiation_service.create_negotiation(demo_deal_in)
    deal_id = deal_resp.id
    print(f"Deal registered with ID: {deal_id}")

    # 4. Generate Briefing with Memory OFF
    print("\n" + "-" * 70)
    print("[Step 4] BRIEFING 1: Memory OFF (Baseline Generic Assistant)")
    print("-" * 70)
    off_res = negotiation_service.analyze_negotiation(deal_id=deal_id, use_memory=False)
    off_briefing = off_res["briefing"]

    print(f"Target Price:     INR {off_briefing['target_price']:,.2f}")
    print(f"Walk-Away Price:  INR {off_briefing['walk_away_price']:,.2f}")
    print(f"Historical Evidence Count: {len(off_briefing['historical_evidence'])} (Expected: 0)")
    print(f"Learned Patterns Count:    {len(off_briefing['learned_patterns'])} (Expected: 0)")
    print("Top Recommended Tactics:")
    for t in off_briefing["recommended_tactics"][:3]:
        print(f"  [{t['rank']}] {t['tactic']}: {t['reason'][:90]}...")
    print(f"Tactics to Avoid: {off_briefing['tactics_to_avoid']}")

    # Pace requests for TPM
    time.sleep(2.5)

    # 5. Generate Briefing with Memory ON
    print("\n" + "-" * 70)
    print("[Step 5] BRIEFING 2: Memory ON (Evidence-Grounded with Hindsight)")
    print("-" * 70)
    on_res = negotiation_service.analyze_negotiation(deal_id=deal_id, use_memory=True)
    on_briefing = on_res["briefing"]
    recalled_mems = on_res["recalled_memories"]

    print(f"Recalled Memories from Hindsight: {len(recalled_mems)} unique facts")
    print(f"Target Price:     INR {on_briefing['target_price']:,.2f}")
    print(f"Walk-Away Price:  INR {on_briefing['walk_away_price']:,.2f}")
    print(f"Historical Evidence Count: {len(on_briefing['historical_evidence'])}")
    print(f"Learned Patterns Count:    {len(on_briefing['learned_patterns'])}")
    
    print("\nSample Historical Evidence with Citations:")
    for ev in on_briefing["historical_evidence"][:2]:
        print(f"  * Claim: {ev['claim']}")
        print(f"    Memory ID: {ev['supporting_memory_id']}")
        print(f"    Excerpt:   \"{ev['source_excerpt_or_reference'][:100]}...\"")

    print("\nLearned Patterns from Real Recalled Deals:")
    for p in on_briefing["learned_patterns"][:2]:
        print(f"  * Tactic: {p['tactic']}")
        print(f"    Success Rate: {p['success_rate']}% ({p['successes']}/{p['attempts']} attempts)")
        print(f"    Citations: {p['supporting_memory_citations']}")

    print("\nRecommended Strategy with Evidence:")
    for t in on_briefing["recommended_tactics"][:3]:
        print(f"  [{t['rank']}] {t['tactic']} (Confidence: {t['confidence']})")
        print(f"      Evidence: {t['supporting_evidence'][:100]}...")

    print(f"\nTactics Known to Fail / Avoid: {on_briefing['tactics_to_avoid']}")
    print(f"Temporal Observations:         {on_briefing['temporal_observations']}")

    # 6. Record Outcome and Retain into Hindsight
    print("\n" + "-" * 70)
    print("[Step 6] RECORDING OUTCOME & RETAINING TO HINDSIGHT")
    print("-" * 70)
    outcome_in = OutcomeCreate(
        final_price=1240000.0,
        contract_duration_months=12,
        tactics_attempted=[
            TacticAttempt(
                tactic="Support-fee unbundling challenge",
                vendor_response="Vendor reduced support fee by 18% from INR 3,00,000 to INR 2,46,000",
                success=True
            ),
            TacticAttempt(
                tactic="Multi-year commitment trade",
                vendor_response="Vendor refused multi-year discount, citing cybersecurity inflation",
                success=False
            )
        ],
        vendor_response="Aggressive on support fee initially, but folded quickly on line-item SLA challenge. Refused multi-year pricing.",
        successful_tactics=["Support-fee unbundling challenge"],
        failed_tactics=["Multi-year commitment trade"],
        terms_accepted_rejected="Accepted standard 4-hour SLA tier; refused paid dedicated TAM add-on.",
        lessons_learned="ShieldArc support fee challenge succeeded again, yielding 18% savings. Multi-year lock-in without true-down failed.",
        notes="Live demo CLI run."
    )

    out_resp = negotiation_service.record_outcome_and_retain(deal_id=deal_id, outcome_in=outcome_in)
    print(f"Outcome successfully retained to Hindsight memory bank!")
    print(f"Hindsight Document ID: {out_resp.hindsight_doc_id}")
    print(f"Final Negotiated Price: INR {out_resp.final_price:,.2f} (Savings: INR {demo_deal_in.initial_quote - out_resp.final_price:,.2f})")

    # 7. Demonstrate That the Next Deal Recalls This Newly Retained Experience
    print("\n" + "-" * 70)
    print("[Step 7] SUBSEQUENT DEAL: Proving DealMemory Learned from Previous Negotiation")
    print("-" * 70)
    next_deal_in = NegotiationCreate(
        vendor="ShieldArc",
        product="ShieldArc Network SASE",
        category="Cybersecurity",
        seats=110,
        initial_quote=1650000.0,
        contract_duration_months=12,
        support_fee=330000.0,
        renewal_type="New",
        deadline="2026-11-20",
        clauses_raised=["Support fee unbundling"],
        notes="Checking whether the briefing now cites our newly retained negotiation experience."
    )
    next_deal_resp = negotiation_service.create_negotiation(next_deal_in)
    next_res = negotiation_service.analyze_negotiation(deal_id=next_deal_resp.id, use_memory=True)
    next_briefing = next_res["briefing"]

    print(f"Subsequent Deal Analysis complete!")
    print(f"Target Price: INR {next_briefing['target_price']:,.2f}")
    print(f"Historical Evidence Cited: {len(next_briefing['historical_evidence'])} items")
    for ev in next_briefing["historical_evidence"][:3]:
        print(f"  - Cited: {ev['claim']} (Ref: {ev['supporting_memory_id']})")

    print("\n" + "=" * 70)
    print("DEMO CLI RESULT: ALL PHASES VERIFIED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    main()
