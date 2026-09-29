"""
DealMemory - Health and System Routes
"""

from fastapi import APIRouter
from backend.services.hindsight_service import hindsight_service
from backend.services.llm_service import llm_service
from backend.database import get_db_connection

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "DealMemory API"}

@router.get("/health/detailed")
def detailed_health_check():
    # 1. SQLite check
    db_ok = False
    db_msg = ""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) as c FROM negotiations")
        c = cursor.fetchone()["c"]
        conn.close()
        db_ok = True
        db_msg = f"SQLite operational ({c} negotiations)"
    except Exception as e:
        db_ok = False
        db_msg = f"SQLite error: {str(e)}"

    # 2. Hindsight check
    hs_ok, hs_msg = hindsight_service.check_connection()

    # 3. Groq check
    gq_ok, gq_msg = llm_service.check_connection()

    all_ready = db_ok and hs_ok and gq_ok

    return {
        "status": "ready" if all_ready else "degraded",
        "services": {
            "sqlite": {
                "status": "connected" if db_ok else "error",
                "message": db_msg
            },
            "hindsight": {
                "status": "connected" if hs_ok else "error",
                "message": hs_msg
            },
            "groq": {
                "status": "connected" if gq_ok else "error",
                "message": gq_msg
            }
        }
    }
