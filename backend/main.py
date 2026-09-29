"""
DealMemory - Backend FastAPI Application
========================================
Main entry point for DealMemory API server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import init_db
from backend.routes.health import router as health_router
from backend.routes.negotiations import router as negotiations_router
from backend.routes.memory import router as memory_router

app = FastAPI(
    title="DealMemory API",
    description="Negotiation intelligence that learns from every deal. Powered by Hindsight Cloud persistent memory.",
    version="1.0.0"
)

# Non-negotiable Rule 11: CORS restricted strictly to the actual frontend origin (no wildcard).
origins = [
    settings.FRONTEND_ORIGIN,
    # Also support common localhost variants if FRONTEND_ORIGIN is local
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
# Deduplicate while preserving order
unique_origins = list(dict.fromkeys([o for o in origins if o]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=unique_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Startup event to ensure SQLite tables exist
@app.on_event("startup")
def on_startup():
    init_db()

# Mount routers
app.include_router(health_router)
app.include_router(negotiations_router)
app.include_router(memory_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
