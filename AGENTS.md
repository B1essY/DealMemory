# DealMemory - Agent Rules and Constraints

## NON-NEGOTIABLES
1. Hindsight IS the memory. All historical/organizational claims come only from real Hindsight recall results. Never use JSON files, arrays, dicts, browser storage, local vector stores or SQLite as substitute memory or as a fallback.
2. SQLite is allowed only for: app metadata, dashboard numbers, evaluation ground truth/results, UI history. It must NEVER be passed to the LLM as organizational memory. (Cross-checking eval counts against SQLite is allowed.)
3. Architecture: current negotiation + Hindsight recall -> LLM -> strategy.
4. Historical evidence (from recall) and AI recommendation (model reasoning) are separate in the JSON schema and visually distinct in the UI.
5. Every historical claim carries a citation to the recalled memory that supports it. Use only IDs/references Hindsight actually returns; if none are stable, build an internal mapping to the exact recalled result and label it internal. Never invent IDs.
6. If recall returns nothing relevant, show EXACTLY: "No relevant organizational experience found." Never say "first time ever". Never say "I remember" unless memory was actually retrieved.
7. Never fabricate negotiations, vendor behavior, prices, savings, success rates or temporal patterns. Temporal observations only if supported by retained data. Weak/conflicting evidence must be stated.
8. If Hindsight or Groq fails: show the real error. If retain fails: never say the memory was saved. If recall fails: show no historical evidence.
9. Secrets only in backend .env. Provide .env.example. Never commit .env. Never expose keys to the frontend. Verify the frontend bundle contains no secrets.
10. Never use the event word formed by joining "h-a-c-k" and "a-t-h-o-n" anywhere: README, UI, code, comments, docs, commit messages, generated content.
11. CORS restricted to the actual frontend origin (no wildcard in the final config).
12. Report evaluation numbers exactly as measured, labelled "Results from a small synthetic test set." No statistical-significance or real-world claims. Never write invented numbers in README or docs; if eval hasn't run, say so.

## STACK
- Backend: Python 3.12+, FastAPI, Pydantic v2, SQLite
- Frontend: React 18+, Vite, TypeScript, Tailwind CSS, Lucide React
- LLM: Groq API with model configured via `GROQ_MODEL` (e.g., `llama-3.3-70b-versatile`), timeout, exponential backoff retry, JSON mode validated by Pydantic
- Memory: Hindsight Cloud, one bank per organization (`HINDSIGHT_BANK_ID`)
- Environment variables:
  - `HINDSIGHT_API_KEY`: API Key for Hindsight Cloud
  - `HINDSIGHT_BANK_ID`: Dedicated bank identifier
  - `HINDSIGHT_BASE_URL`: Hindsight API endpoint (defaults to https://api.hindsight.vectorize.io)
  - `GROQ_API_KEY`: API Key for Groq
  - `GROQ_MODEL`: Model name for Groq (e.g. llama-3.3-70b-versatile)
  - `FRONTEND_ORIGIN`: Allowed frontend origin (e.g. http://localhost:5173)

## DIRECTORY STRUCTURE
- `backend/`
  - `main.py`
  - `config.py`
  - `database.py`
  - `models/`
  - `schemas/`
  - `routes/`
  - `services/`
    - `hindsight_service.py` (ALL Hindsight code lives exclusively here)
    - `llm_service.py`
    - `negotiation_service.py`
    - `eval_service.py`
  - `tests/`
- `frontend/`
  - `src/`
    - `components/`
    - `pages/`
    - `services/`
    - `hooks/`
    - `types/`
    - `App.tsx`
    - `main.tsx`
- `seed/`
  - `negotiations.json` (16 total: 12 seed, 4 held-out)
  - `split.json`
- `evaluation/`
  - `results.json`
- `docs/`
  - `article-notes.md`
  - `screenshots/`
- `scripts/`
  - `spike_hindsight.py`
  - `spike_groq.py`
  - `demo_cli.py`
- `PROGRESS.md`
- `AGENTS.md`
- `.env.example`
- `.gitignore`
- `README.md`
