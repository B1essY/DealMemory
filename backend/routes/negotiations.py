"""
DealMemory - Negotiations and Briefings Routes
"""

from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Optional
from backend.schemas.deal import (
    NegotiationCreate,
    NegotiationResponse,
    AnalyzeRequest,
    OutcomeCreate,
    OutcomeResponse
)
from backend.services.negotiation_service import negotiation_service

router = APIRouter(prefix="/api/negotiations", tags=["Negotiations"])

@router.post("", response_model=NegotiationResponse)
def create_negotiation(deal: NegotiationCreate):
    try:
        return negotiation_service.create_negotiation(deal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[NegotiationResponse])
def list_negotiations():
    try:
        return negotiation_service.list_negotiations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=NegotiationResponse)
def get_negotiation(id: str = Path(..., description="Negotiation deal ID")):
    deal = negotiation_service.get_negotiation(id)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Negotiation deal '{id}' not found")
    return deal

@router.post("/{id}/analyze")
def analyze_negotiation(id: str, request: AnalyzeRequest):
    """
    Produces a negotiation briefing.
    request.use_memory = True -> Hindsight memory active (ON)
    request.use_memory = False -> Baseline generic procurement (OFF)
    """
    try:
        result = negotiation_service.analyze_negotiation(
            deal_id=id,
            use_memory=request.use_memory
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/{id}/outcome", response_model=OutcomeResponse)
def record_outcome(id: str, outcome: OutcomeCreate):
    """
    Records final outcome, builds narrative memory, retains into Hindsight,
    verifies recallability, and logs metadata.
    """
    try:
        return negotiation_service.record_outcome_and_retain(id, outcome)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outcome retention failed: {str(e)}")

@router.post("/{id}/retain")
def trigger_manual_retain(id: str):
    """
    Re-retains an existing negotiation's ground-truth outcome into Hindsight.
    Idempotent via document_id upsert.
    """
    deal = negotiation_service.get_negotiation(id)
    if not deal:
        raise HTTPException(status_code=404, detail=f"Deal '{id}' not found")
    
    # Check if deal has an outcome in SQLite
    from backend.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM outcomes WHERE negotiation_id = ?", (id,))
    out_row = cursor.fetchone()
    conn.close()

    if not out_row:
        raise HTTPException(status_code=400, detail="Cannot retain deal without an outcome.")

    # Re-retain using narrative
    from backend.services.hindsight_service import hindsight_service
    doc_id = f"dealmemory-negotiation-{id}"
    content = (
        f"Negotiation experience with {deal['vendor']} for {deal['product']} on {deal['deadline']}. "
        f"Initial quote: INR {deal['initial_quote']:,.2f}. Agreed final price: INR {out_row['final_price']:,.2f}. "
        f"Vendor behavior: {out_row['vendor_response']}. Lessons learned: {out_row['lessons_learned']}."
    )
    try:
        res = hindsight_service.retain_negotiation(
            document_id=doc_id,
            content=content,
            context=f"SaaS negotiation outcome - {deal['vendor']}",
            timestamp=f"{deal['deadline']}T12:00:00Z"
        )
        return {"status": "retained", "doc_id": doc_id, "hindsight_result": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retain failed: {str(e)}")
