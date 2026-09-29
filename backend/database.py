"""
DealMemory SQLite Database Layer
CRITICAL NON-NEGOTIABLE RULE:
SQLite is allowed only for: app metadata, dashboard numbers, evaluation ground truth/results, UI history.
It must NEVER be passed to the LLM as organizational memory.
All organizational memory is strictly retrieved from Hindsight.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from backend.config import settings

def get_db_connection():
    db_path = Path(settings.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Negotiations metadata table (UI tracking only)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS negotiations (
        id TEXT PRIMARY KEY,
        vendor TEXT NOT NULL,
        product TEXT NOT NULL,
        category TEXT NOT NULL,
        seats INTEGER NOT NULL,
        initial_quote REAL NOT NULL,
        contract_duration_months INTEGER NOT NULL,
        support_fee REAL NOT NULL,
        renewal_type TEXT NOT NULL,
        deadline TEXT NOT NULL,
        clauses_raised TEXT, -- JSON array
        notes TEXT,
        is_analyzed INTEGER DEFAULT 0,
        is_seeded INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)
    
    # 2. Briefings history (UI comparison only, NOT agent memory)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS briefings (
        id TEXT PRIMARY KEY,
        negotiation_id TEXT NOT NULL,
        use_memory INTEGER NOT NULL,
        model_used TEXT NOT NULL,
        raw_recall_count INTEGER DEFAULT 0,
        briefing_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (negotiation_id) REFERENCES negotiations (id)
    )
    """)
    
    # 3. Outcomes table (Audit & UI tracking only)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS outcomes (
        id TEXT PRIMARY KEY,
        negotiation_id TEXT NOT NULL,
        final_price REAL NOT NULL,
        contract_duration_months INTEGER,
        tactics_attempted TEXT, -- JSON array
        vendor_response TEXT,
        successful_tactics TEXT, -- JSON array
        failed_tactics TEXT, -- JSON array
        terms_accepted_rejected TEXT,
        lessons_learned TEXT,
        notes TEXT,
        retained_to_hindsight INTEGER DEFAULT 0,
        hindsight_doc_id TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (negotiation_id) REFERENCES negotiations (id)
    )
    """)
    
    # 4. Seed manifest (Tracks which seed items were retained to Hindsight)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seed_manifest (
        deal_id TEXT PRIMARY KEY,
        doc_id TEXT NOT NULL,
        retained_at TEXT NOT NULL,
        verified_at TEXT
    )
    """)
    
    # 5. Evaluation runs (ground truth & computed metrics store)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eval_runs (
        id TEXT PRIMARY KEY,
        run_date TEXT NOT NULL,
        results_json TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
