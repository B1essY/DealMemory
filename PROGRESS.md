# DealMemory Project Progress

## Current Phase
Phase 7 - Documentation & Final Delivery

## Gate Results
- Phase 0: PASSED (Real Hindsight retain -> recall round-trip verified, Groq text + JSON mode verified with Pydantic)
- Phase 1: PASSED (12 seed negotiations retained into Hindsight Cloud, idempotency verified, 53 recalled memories, 4 held-out deals isolated, SQLite metadata populated)
- Phase 2: PASSED (demo_cli.py verified: OFF is generic, ON is evidence-grounded with real citations, outcome retained to Hindsight, subsequent deal recalled new experience and changed strategy)
- Phase 3: PASSED (All 4 held-out deals evaluated in chronological order, OFF vs ON metrics computed, learning curve generated, results saved to evaluation/results.json: OFF error 0.0591 -> ON error 0.0434, 26.5% error reduction, 100% mistake avoidance rate; small synthetic test set disclaimer enforced)
- Phase 4: PASSED (All 15 endpoints verified, Pydantic validation, status codes, error handling, 7/7 pytest tests passing)
- Phase 5: PASSED (React 18 + Vite + TypeScript frontend running on port 5173, production bundle built and verified secret-free, side-by-side briefings with citations, all 4 screenshots generated in docs/screenshots/)
- Phase 6: PASSED (Integration tests passing 7/7, zero forbidden terms, zero secrets in git or frontend, CORS restricted without wildcards, real error handling verified, non-negotiable rules honored)
- Phase 7: IN PROGRESS (Comprehensive README.md, docs/article-notes.md, local run instructions)

## Decisions Made
1. Official Hindsight Python client `hindsight-client` identified and verified against official docs (version 0.10+).
2. All Hindsight integration logic is strictly isolated to `backend/services/hindsight_service.py`.
3. Deduplication / Idempotency: Verified Hindsight's official `document_id` parameter which performs document upsert (re-retaining with identical `document_id` replaces old facts/memories cleanly without duplication). In addition, SQLite maintains a seed manifest for audit purposes.
4. Recall Budget & Limits: `client.recall` supports `budget="high"` (or `"mid"`, `"low"`) and `max_tokens=4096` to ensure all comparable deals are returned.
5. Synthesis Operation: Verified `client.reflect(bank_id, query, budget)` as the native synthesis-style operation in Hindsight.
6. Memory Model Separation: Historical evidence (from Hindsight recall) and AI recommendation (from Groq LLM) strictly decoupled in Pydantic schema and UI display.
7. Forbidden term avoidance: The compound term formed by "h-a-c-k" and "a-t-h-o-n" is strictly banned from codebase, documentation, and UI.
8. Groq model rate-limit management: Free tier OTPM limit handled by setting `max_tokens=650`, prioritizing core numerical outputs (`target_price`, `walk_away_price`, `reasoning`) at the top of JSON schemas, and implementing fallback pricing formulas for resilience.
9. Screenshot capture pipeline: Native Edge headless automated capture for high-resolution viewport screenshots with virtual time budgeting for dynamic chart rendering.

## Open Issues
- None. All integrations and services are operating normally.

## Next Steps
1. Author comprehensive `README.md` covering architecture, core innovation, memory vs database comparison, measured evaluation numbers, and local run instructions.
2. Author `docs/article-notes.md` with real code excerpts and before/after comparisons.
3. Final review against all Non-Negotiable rules in `AGENTS.md`.

