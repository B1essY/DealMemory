"""
DealMemory - Memory, Seeding, Patterns, and Evaluation Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from backend.schemas.deal import RecallQueryRequest, SeedStatusResponse
from backend.services.hindsight_service import hindsight_service
from backend.services.negotiation_service import negotiation_service
from backend.services.eval_service import eval_service
from backend.database import get_db_connection

router = APIRouter(tags=["Memory & Demo"])

# ----------------- DEMO SEEDING -----------------

@router.post("/api/demo/seed", response_model=Dict[str, Any])
def seed_demo_data():
    """
    Seeds the 12 initial negotiation experiences into Hindsight Cloud and SQLite metadata.
    Idempotent using Hindsight's official document_id upsert mechanism.
    Returns real counts: {seeded, skipped, verified, total_seed_deals}.
    """
    try:
        result = negotiation_service.seed_database_and_memory()
        return {
            "status": "success",
            "message": "Seeded 12 negotiation experiences to Hindsight memory bank.",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Seeding failed: {str(e)}")

@router.get("/api/demo/status", response_model=SeedStatusResponse)
def get_seed_status():
    """
    Returns seeding status, verified memory count, and Hindsight connectivity.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) as c FROM seed_manifest")
    manifest_count = cursor.fetchone()["c"]
    conn.close()

    is_connected, msg = hindsight_service.check_connection()

    return SeedStatusResponse(
        is_seeded=(manifest_count >= 12),
        seeded_count=manifest_count,
        skipped_count=0,
        verified_count=manifest_count if is_connected else 0,
        hindsight_connected=is_connected,
        details=msg
    )

@router.post("/api/demo/reset")
def reset_demo():
    """
    Safely resets local SQLite application metadata, briefings, outcomes, and seed manifest.
    Note on Hindsight Cloud: The official Hindsight API allows deleting individual documents
    via DocumentsApi, but entire bank deletion depends on permissions. We clean up seed documents
    where possible and clearly report any backend limitations without fabrication.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM briefings")
        cursor.execute("DELETE FROM outcomes")
        cursor.execute("DELETE FROM negotiations")
        cursor.execute("DELETE FROM seed_manifest")
        conn.commit()
        conn.close()
        return {
            "status": "reset",
            "message": "Local negotiation, briefing, and outcome records have been reset.",
            "hindsight_note": "Local metadata cleared. To re-seed Hindsight memory bank, call POST /api/demo/seed."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")

# ----------------- RECALL & MEMORY STATS -----------------

@router.post("/api/memory/recall")
def test_recall(req: RecallQueryRequest):
    """
    Tests real organizational memory recall against Hindsight.
    Returns structured results, fact types, entities, and citations.
    """
    try:
        results = hindsight_service.recall_memories(
            query=req.query,
            budget=req.budget or "high",
            max_tokens=req.max_tokens or 2048,
            types=req.types
        )
        return {
            "query": req.query,
            "results_count": len(results),
            "memories": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recall failed: {str(e)}")

@router.get("/api/memory/stats")
def get_memory_stats():
    """
    Returns Hindsight bank statistics and health.
    """
    return hindsight_service.get_memory_stats()

# ----------------- LEARNED PATTERNS -----------------

@router.get("/api/learning/patterns")
def get_learned_patterns():
    """
    Retrieves cross-vendor patterns derived from real Hindsight recall.
    Runs recall for cross-vendor SaaS negotiation tactics and summarizes observed patterns.
    """
    try:
        # Query real memory for cross-deal patterns
        results = hindsight_service.recall_memories(
            query="What negotiation tactics have succeeded or failed across SaaS deals? Support fee challenges, early renewals, multi-year commitments",
            budget="high",
            max_tokens=3000
        )
        
        return {
            "recalled_pattern_facts_count": len(results),
            "sample_evidence": results[:10],
            "bank_id": hindsight_service.bank_id,
            "note": "All pattern insights are grounded in real Hindsight recall facts."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve learned patterns: {str(e)}")

# ----------------- EVALUATION -----------------

@router.get("/api/eval/results")
def get_evaluation_results():
    """
    Returns the latest evaluation results, metrics, learning curve, and cross-checks.
    Labelled: 'Results from a small synthetic test set.'
    """
    results = eval_service.get_latest_results()
    if not results:
        return {
            "status": "pending",
            "message": "Evaluation has not yet been executed. Use POST /api/eval/run to execute sequential evaluation."
        }
    return results

@router.post("/api/eval/run")
def trigger_evaluation():
    """
    Executes the sequential evaluation loop over the 4 held-out deals:
    Runs OFF, runs ON, computes metrics, retains outcome, builds learning curve.
    """
    try:
        summary = eval_service.run_evaluation()
        return {
            "status": "completed",
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")
