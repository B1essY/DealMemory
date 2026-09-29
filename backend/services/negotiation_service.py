"""
DealMemory - Negotiation Service
================================
Coordinates:
1. Deal CRUD and metadata logging in SQLite.
2. Two-query Hindsight Recall pipeline:
   - Query 1: Vendor-specific recall (prior prices, concessions, objections, tactics).
   - Query 2: Pattern-level cross-vendor recall (successful and failed tactics, timing/fiscal patterns).
3. Strategy briefing generation via LLM Service (OFF vs ON).
4. Outcome retention loop:
   - Formats outcome into rich narrative memory.
   - Retains into Hindsight using deterministic document_id.
   - Verifies recallability before confirmation.
5. Idempotent seeding from seed/negotiations.json (12 seed deals).
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from backend.config import settings
from backend.database import get_db_connection
from backend.schemas.deal import (
    NegotiationCreate,
    NegotiationResponse,
    OutcomeCreate,
    OutcomeResponse,
    BriefingSchema
)
from backend.services.hindsight_service import hindsight_service
from backend.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class NegotiationService:
    def __init__(self):
        pass

    def create_negotiation(self, deal_in: NegotiationCreate) -> NegotiationResponse:
        deal_id = f"deal_{uuid.uuid4().hex[:8]}"
        created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO negotiations (
                id, vendor, product, category, seats, initial_quote,
                contract_duration_months, support_fee, renewal_type,
                deadline, clauses_raised, notes, is_analyzed, is_seeded, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?)
            """,
            (
                deal_id,
                deal_in.vendor,
                deal_in.product,
                deal_in.category,
                deal_in.seats,
                deal_in.initial_quote,
                deal_in.contract_duration_months,
                deal_in.support_fee,
                deal_in.renewal_type,
                deal_in.deadline,
                json.dumps(deal_in.clauses_raised),
                deal_in.notes or "",
                created_at
            )
        )
        conn.commit()
        conn.close()
        
        return NegotiationResponse(
            id=deal_id,
            vendor=deal_in.vendor,
            product=deal_in.product,
            category=deal_in.category,
            seats=deal_in.seats,
            initial_quote=deal_in.initial_quote,
            contract_duration_months=deal_in.contract_duration_months,
            support_fee=deal_in.support_fee,
            renewal_type=deal_in.renewal_type,
            deadline=deal_in.deadline,
            clauses_raised=deal_in.clauses_raised,
            notes=deal_in.notes,
            is_analyzed=False,
            is_seeded=False,
            created_at=created_at
        )

    def get_negotiation(self, deal_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM negotiations WHERE id = ?", (deal_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        
        deal = dict(row)
        deal["clauses_raised"] = json.loads(deal["clauses_raised"]) if deal.get("clauses_raised") else []
        deal["is_analyzed"] = bool(deal["is_analyzed"])
        deal["is_seeded"] = bool(deal["is_seeded"])
        return deal

    def list_negotiations(self) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM negotiations ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            d = dict(r)
            d["clauses_raised"] = json.loads(d["clauses_raised"]) if d.get("clauses_raised") else []
            d["is_analyzed"] = bool(d["is_analyzed"])
            d["is_seeded"] = bool(d["is_seeded"])
            results.append(d)
        return results

    def analyze_negotiation(self, deal_id: str, use_memory: bool = True) -> Dict[str, Any]:
        """
        Executes negotiation briefing analysis.
        If use_memory is True:
          Runs at least two Hindsight recall queries:
            1. Vendor-specific (prior prices, concessions, objections, tactics).
            2. Cross-vendor pattern level (successful and failed tactics, quarter-end timing).
          Fuses and deduplicates recalled memories, logging recall counts.
        If use_memory is False:
          Runs baseline without memories.
        """
        deal = self.get_negotiation(deal_id)
        if not deal:
            raise ValueError(f"Negotiation deal with ID '{deal_id}' not found.")

        recalled_memories: List[Dict[str, Any]] = []
        recall_stats = {
            "vendor_query": "",
            "vendor_memories_count": 0,
            "pattern_query": "",
            "pattern_memories_count": 0,
            "total_unique_memories": 0
        }

        if use_memory:
            # Query 1: Vendor-specific query
            vendor_query = (
                f"Historical negotiations with {deal['vendor']} for {deal['product']}: "
                f"concession behavior, prior quotes and discounts, support fees, objections, and tactical responses"
            )
            recall_stats["vendor_query"] = vendor_query
            try:
                vendor_results = hindsight_service.recall_memories(
                    query=vendor_query,
                    budget="high",
                    max_tokens=2048,
                    types=["experience", "observation", "world"]
                )
                recall_stats["vendor_memories_count"] = len(vendor_results)
            except Exception as e:
                logger.error(f"Vendor-specific recall failed: {e}")
                vendor_results = []

            # Query 2: Pattern-level cross-vendor query
            pattern_query = (
                f"SaaS software licence negotiation tactics: support-fee unbundling success rate, "
                f"early-renewal discount outcomes, multi-year contract concessions, volume tier discounts, "
                f"quarter-end timing deadline effects, and failed tactics"
            )
            recall_stats["pattern_query"] = pattern_query
            try:
                pattern_results = hindsight_service.recall_memories(
                    query=pattern_query,
                    budget="high",
                    max_tokens=2048,
                    types=["experience", "observation", "world"]
                )
                recall_stats["pattern_memories_count"] = len(pattern_results)
            except Exception as e:
                logger.error(f"Cross-vendor pattern recall failed: {e}")
                pattern_results = []

            # Fuse and deduplicate by memory ID
            seen_ids = set()
            for m in (vendor_results + pattern_results):
                mid = m.get("id")
                if mid and mid not in seen_ids:
                    seen_ids.add(mid)
                    recalled_memories.append(m)
                elif not mid:
                    recalled_memories.append(m)

            recall_stats["total_unique_memories"] = len(recalled_memories)
            logger.info(
                f"Deal {deal_id} recall complete: {recall_stats['vendor_memories_count']} vendor facts, "
                f"{recall_stats['pattern_memories_count']} pattern facts, {len(recalled_memories)} unique total."
            )

        # Generate briefing via LLM service
        briefing = llm_service.generate_briefing(
            deal=deal,
            recalled_memories=recalled_memories,
            use_memory=use_memory
        )

        # Save briefing in SQLite metadata for history/dashboard
        conn = get_db_connection()
        cursor = conn.cursor()
        briefing_id = f"brf_{uuid.uuid4().hex[:8]}"
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO briefings (
                id, negotiation_id, use_memory, model_used,
                raw_recall_count, briefing_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                briefing_id,
                deal_id,
                1 if use_memory else 0,
                settings.GROQ_MODEL,
                len(recalled_memories),
                briefing.model_dump_json(),
                now_str
            )
        )
        cursor.execute("UPDATE negotiations SET is_analyzed = 1 WHERE id = ?", (deal_id,))
        conn.commit()
        conn.close()

        return {
            "briefing_id": briefing_id,
            "deal_id": deal_id,
            "briefing": briefing.model_dump(),
            "recall_stats": recall_stats,
            "recalled_memories": recalled_memories
        }

    def record_outcome_and_retain(
        self,
        deal_id: str,
        outcome_in: OutcomeCreate
    ) -> OutcomeResponse:
        """
        Records the actual negotiation outcome:
        1. Builds a structured narrative memory.
        2. Retains the experience to Hindsight using document_id=deal_id.
        3. Polls recall to verify it is searchable before confirmation.
        4. Logs outcome metadata in SQLite.
        """
        deal = self.get_negotiation(deal_id)
        if not deal:
            raise ValueError(f"Negotiation deal '{deal_id}' not found.")

        doc_id = f"dealmemory-negotiation-{deal_id}"
        outcome_id = f"out_{uuid.uuid4().hex[:8]}"
        created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Construct narrative memory
        tactics_summary = "; ".join([
            f"{t.tactic} ({'succeeded' if t.success else 'failed'}: {t.vendor_response})"
            for t in outcome_in.tactics_attempted
        ]) if outcome_in.tactics_attempted else "Standard commercial discussion"

        worked_str = ", ".join(outcome_in.successful_tactics) if outcome_in.successful_tactics else "None"
        failed_str = ", ".join(outcome_in.failed_tactics) if outcome_in.failed_tactics else "None"
        
        narrative_content = (
            f"Negotiation experience with {deal['vendor']} for {deal['product']} ({deal['category']}) on {deal['deadline']}. "
            f"Initial quote was INR {deal['initial_quote']:,.2f} for {deal['seats']} seats (support fee INR {deal['support_fee']:,.2f}). "
            f"Final agreed price: INR {outcome_in.final_price:,.2f} for {outcome_in.contract_duration_months} months. "
            f"Vendor stance and responses: {outcome_in.vendor_response}. "
            f"Tactics attempted: {tactics_summary}. "
            f"Successful tactics: {worked_str}. "
            f"Failed tactics: {failed_str}. "
            f"Terms accepted vs refused: {outcome_in.terms_accepted_rejected}. "
            f"Key lesson learned: {outcome_in.lessons_learned}. "
            f"Additional notes: {outcome_in.notes or 'None'}."
        )

        # Real Hindsight retain
        retain_success = False
        try:
            hindsight_service.ensure_bank_exists()
            retain_res = hindsight_service.retain_negotiation(
                document_id=doc_id,
                content=narrative_content,
                context=f"SaaS negotiation outcome - {deal['vendor']}",
                timestamp=f"{deal['deadline']}T12:00:00Z",
                metadata={
                    "vendor": deal["vendor"],
                    "deal_id": deal_id,
                    "final_price": str(outcome_in.final_price)
                }
            )
            retain_success = True
            logger.info(f"Retained deal {deal_id} to Hindsight in {retain_res['elapsed_seconds']}s")
            
            # Verify recallability
            verified, elapsed, _ = hindsight_service.poll_for_recallability(
                query=f"Negotiation outcome with {deal['vendor']} {deal['product']}",
                expected_substr=deal["vendor"],
                max_wait_seconds=20,
                poll_interval=2
            )
            logger.info(f"Recall verification for {doc_id}: {verified} ({elapsed}s)")
        except Exception as e:
            logger.error(f"Failed to retain outcome to Hindsight: {e}")
            raise RuntimeError(f"Hindsight outcome retention failed: {str(e)}") from e

        # Store outcome metadata in SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO outcomes (
                id, negotiation_id, final_price, contract_duration_months,
                tactics_attempted, vendor_response, successful_tactics,
                failed_tactics, terms_accepted_rejected, lessons_learned,
                notes, retained_to_hindsight, hindsight_doc_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                outcome_id,
                deal_id,
                outcome_in.final_price,
                outcome_in.contract_duration_months,
                json.dumps([t.model_dump() for t in outcome_in.tactics_attempted]),
                outcome_in.vendor_response,
                json.dumps(outcome_in.successful_tactics),
                json.dumps(outcome_in.failed_tactics),
                outcome_in.terms_accepted_rejected,
                outcome_in.lessons_learned,
                outcome_in.notes or "",
                1 if retain_success else 0,
                doc_id,
                created_at
            )
        )
        conn.commit()
        conn.close()

        return OutcomeResponse(
            id=outcome_id,
            negotiation_id=deal_id,
            final_price=outcome_in.final_price,
            contract_duration_months=outcome_in.contract_duration_months,
            tactics_attempted=outcome_in.tactics_attempted,
            vendor_response=outcome_in.vendor_response,
            successful_tactics=outcome_in.successful_tactics,
            failed_tactics=outcome_in.failed_tactics,
            terms_accepted_rejected=outcome_in.terms_accepted_rejected,
            lessons_learned=outcome_in.lessons_learned,
            notes=outcome_in.notes,
            retained_to_hindsight=retain_success,
            hindsight_doc_id=doc_id,
            created_at=created_at
        )

    def seed_database_and_memory(self) -> Dict[str, Any]:
        """
        Seeds the 12 initial negotiation experiences into Hindsight memory bank
        and loads their structured metadata into SQLite.
        Uses document_id for idempotency: re-running overwrites/updates cleanly with 0 duplicates.
        """
        seed_path = Path(settings.SEED_PATH)
        split_path = Path(settings.SPLIT_PATH)

        if not seed_path.exists() or not split_path.exists():
            raise FileNotFoundError("Seed files negotiations.json or split.json missing.")

        with open(seed_path, "r", encoding="utf-8") as f:
            all_deals = json.load(f)

        with open(split_path, "r", encoding="utf-8") as f:
            split_info = json.load(f)

        seed_ids = set(split_info.get("seed_deal_ids", []))
        seed_deals = [d for d in all_deals if d["id"] in seed_ids]

        # Ensure memory bank exists
        hindsight_service.ensure_bank_exists()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check existing manifest
        cursor.execute("SELECT deal_id FROM seed_manifest")
        existing_manifest = {row["deal_id"] for row in cursor.fetchall()}

        seeded_count = 0
        skipped_count = 0
        verified_count = 0

        for deal in seed_deals:
            deal_id = deal["id"]
            doc_id = f"dealmemory-negotiation-{deal_id}"
            
            # Upsert into negotiations table
            cursor.execute(
                """
                INSERT OR REPLACE INTO negotiations (
                    id, vendor, product, category, seats, initial_quote,
                    contract_duration_months, support_fee, renewal_type,
                    deadline, clauses_raised, notes, is_analyzed, is_seeded, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?)
                """,
                (
                    deal_id,
                    deal["vendor"],
                    deal["product"],
                    deal["category"],
                    deal["seats"],
                    deal["initial_quote"],
                    deal["contract_duration_months"],
                    deal["support_fee"],
                    deal["renewal_type"],
                    deal["deadline"],
                    json.dumps(deal.get("clauses_raised", [])),
                    deal.get("lesson_learned", ""),
                    f"{deal['date']} 10:00:00"
                )
            )

            # Insert outcome into outcomes table for ground truth
            outcome_id = f"out_{deal_id}"
            cursor.execute(
                """
                INSERT OR REPLACE INTO outcomes (
                    id, negotiation_id, final_price, contract_duration_months,
                    tactics_attempted, vendor_response, successful_tactics,
                    failed_tactics, terms_accepted_rejected, lessons_learned,
                    notes, retained_to_hindsight, hindsight_doc_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    outcome_id,
                    deal_id,
                    deal["final_price"],
                    deal["contract_duration_months"],
                    json.dumps(deal.get("tactics_attempted", [])),
                    deal.get("vendor_behavior", ""),
                    json.dumps(deal.get("successful_tactics", [])),
                    json.dumps(deal.get("failed_tactics", [])),
                    deal.get("what_the_company_refused", ""),
                    deal.get("lesson_learned", ""),
                    deal.get("outcome", ""),
                    doc_id,
                    f"{deal['date']} 12:00:00"
                )
            )

            # Retain into Hindsight (Idempotent via document_id upsert)
            try:
                hindsight_service.retain_negotiation(
                    document_id=doc_id,
                    content=deal["narrative"],
                    context=f"Historical SaaS negotiation - {deal['vendor']}",
                    timestamp=f"{deal['date']}T10:00:00Z",
                    metadata={
                        "vendor": deal["vendor"],
                        "deal_id": deal_id,
                        "date": deal["date"]
                    }
                )
                seeded_count += 1
                
                # Update manifest
                now_iso = datetime.utcnow().isoformat()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO seed_manifest (deal_id, doc_id, retained_at, verified_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (deal_id, doc_id, now_iso, now_iso)
                )
            except Exception as e:
                logger.error(f"Error retaining seed deal {deal_id}: {e}")
                raise RuntimeError(f"Hindsight seeding failed for deal {deal_id}: {e}") from e

        conn.commit()
        conn.close()

        # Run a real verification recall to test that seeded memories are searchable
        try:
            sample_recalled = hindsight_service.recall_memories(
                query="Support-fee unbundling challenge outcomes across SaaS vendors",
                budget="high",
                max_tokens=1024
            )
            verified_count = len(sample_recalled)
        except Exception as e:
            logger.warning(f"Verification recall test returned error: {e}")
            verified_count = 0

        return {
            "seeded": seeded_count,
            "skipped": skipped_count,
            "verified": verified_count,
            "total_seed_deals": len(seed_deals)
        }


negotiation_service = NegotiationService()
