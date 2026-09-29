"""
DealMemory Backend Configuration
Loads environment variables and configuration settings.
All secret keys are managed strictly on the backend.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

ROOT_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    HINDSIGHT_API_KEY: str = Field(default="", description="Hindsight Cloud API Key")
    HINDSIGHT_BANK_ID: str = Field(default="dealmemory-org-prod", description="Organization Memory Bank ID")
    HINDSIGHT_BASE_URL: str = Field(default="https://api.hindsight.vectorize.io", description="Hindsight Base URL")
    
    GROQ_API_KEY: str = Field(default="", description="Groq API Key")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", description="Groq Model name")
    
    FRONTEND_ORIGIN: str = Field(default="http://localhost:5173", description="Allowed CORS Origin")
    
    DATABASE_PATH: str = Field(
        default=str(ROOT_DIR / "dealmemory.db"),
        description="Path to SQLite metadata database"
    )
    
    SEED_PATH: str = Field(
        default=str(ROOT_DIR / "seed" / "negotiations.json"),
        description="Path to seed negotiations dataset"
    )
    
    SPLIT_PATH: str = Field(
        default=str(ROOT_DIR / "seed" / "split.json"),
        description="Path to train/eval split metadata"
    )
    
    EVAL_RESULTS_PATH: str = Field(
        default=str(ROOT_DIR / "evaluation" / "results.json"),
        description="Path to evaluation results storage"
    )

    class Config:
        env_file = (ROOT_DIR / ".env", ROOT_DIR / "backend" / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
