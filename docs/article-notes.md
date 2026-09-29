# DealMemory - Engineering Notes & Architectural Retrospective

> **Summary**: Comprehensive technical analysis of the design, implementation, and empirical evaluation of **DealMemory**, an AI-powered SaaS procurement negotiation intelligence system backed by **Hindsight Cloud** persistent organizational memory and **Groq** high-throughput inference.

---

## 1. Key Technical Decisions & Architecture

### 1.1 The Fundamental Thesis: Memory Over Model
In enterprise procurement, every vendor interaction contains proprietary leverage points:
- What concessions did NimbusCRM yield at Q3 quarter-end?
- Does TracePeak agree to waive their mandatory 18% enterprise support fee when threatened with Datadog migration?
- How does PeoplePulse respond to multi-year prepayment versus annual co-terming?

Generic LLMs (regardless of parameter count) treat every negotiation as day zero. Standard RAG over static documents (PDF contracts, invoice tables) fails because procurement intelligence is **relational, dynamic, and temporal**: deals supersede one another, concessions decay, and tactics that succeeded two years ago may fail in current market cycles.

**DealMemory** separates the architecture into three clean layers:
1. **Organizational Memory Layer (Hindsight Cloud)**: The single source of truth for historical negotiations, vendor behaviors, concession thresholds, and procedural outcomes.
2. **Reasoning & Synthesis Layer (Groq LLM)**: Synthesizes recalled historical evidence with current deal parameters into a structured, executable negotiation briefing.
3. **Application & Ground-Truth Layer (FastAPI + SQLite + React)**: Tracks active deal state, UI history, audit trails, and strict evaluation metrics. SQLite is strictly barred from serving as memory to the LLM.

```
+-------------------------------------------------------------------------+
|                        CURRENT NEGOTIATION DEAL                         |
| (Vendor: NimbusCRM, Seats: 450, Quote: $185k, Support: 18%, Q3 Renewal) |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                      2-QUERY HINDSIGHT RECALL                           |
|  Query 1: Vendor-specific concessions, prior discounts, objection styles|
|  Query 2: Cross-vendor tactic patterns (support unbundling, early locks)|
+------------------------------------+------------------------------------+
                                     |
                         [Fused Recalled Memories]
                         (IDs: 8f2b7a..., 3c19e4...)
                                     |
                                     v
+------------------------------------+------------------------------------+
|                         GROQ INFERENCE ENGINE                           |
|   (qwen/qwen3.8-27b with Pydantic JSON validation & citation mapping)   |
+------------------------------------+------------------------------------+
                                     |
                                     v
+------------------------------------+------------------------------------+
|                   DUAL BRIEFING GENERATION (UI)                         |
|                                                                         |
|  [MEMORY OFF]                              [MEMORY ON]                  |
|  - Target: $165,000 (Generic -10%)         - Target: $148,000           |
|  - 0 Citations                             - Cites Memory #8f2b7a...    |
|  - High variance / guesswork               - "Nimbus waives 18% support |
|                                              fee when 24mo prepaid"     |
+------------------------------------+------------------------------------+
                                     |
                         [Execute Real Deal Outcome]
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  HINDSIGHT RETAIN (POST-NEGOTIATION)                    |
|   Retains deal outcome, successful/failed tactics, final agreed price   |
|   Idempotent doc_id: dealmemory-negotiation-{deal_id}                   |
|   -> Immediately available for future recall across organization        |
+-------------------------------------------------------------------------+
```

---

## 2. Code Snippets That Matter (Production Implementations)

### 2.1 Real Experience Retention (`backend/services/hindsight_service.py`)
No simulated vectors or local JSON mocks. Experiences are formatted with semantic structure, timestamped, and dispatched to Hindsight Cloud via the official SDK:

```python
def retain_experience(
    self,
    content: str,
    document_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    event_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retains a structured negotiation experience into Hindsight Cloud bank.
    Uses document_id for idempotent updates: re-retaining with the same doc_id
    updates existing facts rather than generating duplicate memories.
    """
    client = self._get_client()
    bank_id = self._get_bank_id()

    payload = {
        "bank_id": bank_id,
        "content": content,
    }
    if document_id:
        payload["document_id"] = document_id
    if metadata:
        payload["metadata"] = metadata
    if event_date:
        payload["event_date"] = event_date

    try:
        response = client.retain(**payload)
        logger.info(f"Retained experience to Hindsight bank '{bank_id}' with doc_id: {document_id}")
        return {
            "status": "success",
            "bank_id": bank_id,
            "document_id": document_id,
            "response": str(response)
        }
    except Exception as e:
        logger.error(f"Failed to retain experience in Hindsight: {e}")
        raise
```

### 2.2 Multi-Budget Semantic Recall (`backend/services/hindsight_service.py`)
Memories are fetched with high-budget semantic depth across experience, observation, and world fact types:

```python
def recall_memories(
    self,
    query: str,
    budget: str = "high",
    max_tokens: int = 4096,
    types: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Recalls organizational experiences matching the semantic query.
    Extracts real fact IDs and confidence scores from Hindsight Cloud.
    """
    client = self._get_client()
    bank_id = self._get_bank_id()

    try:
        kwargs = {
            "bank_id": bank_id,
            "query": query,
            "budget": budget,
            "max_tokens": max_tokens,
        }
        if types:
            kwargs["types"] = types

        result = client.recall(**kwargs)
        
        memories = []
        # Parse official Hindsight recall response structure
        items = getattr(result, "memories", None) or getattr(result, "results", None) or []
        for item in items:
            memories.append({
                "id": str(getattr(item, "id", getattr(item, "memory_id", "unknown"))),
                "text": str(getattr(item, "text", getattr(item, "content", ""))),
                "type": str(getattr(item, "type", "experience")),
                "score": float(getattr(item, "score", getattr(item, "confidence", 1.0))),
                "event_date": str(getattr(item, "event_date", "")),
                "metadata": getattr(item, "metadata", {})
            })
        return memories
    except Exception as e:
        logger.error(f"Hindsight recall error: {e}")
        raise
```

### 2.3 Two-Query Recall Fusion (`backend/services/negotiation_service.py`)
A single naive search either gets overwhelmed with broad advice or misses specific vendor idiosyncrasies. DealMemory queries two orthogonal planes and fuses them:

```python
# Query 1: Vendor-specific query (tactics, past quotes, objections)
vendor_query = (
    f"Historical negotiations with {deal['vendor']} for {deal['product']}: "
    f"concession behavior, prior quotes and discounts, support fees, objections, and tactical responses"
)
vendor_results = hindsight_service.recall_memories(
    query=vendor_query, budget="high", max_tokens=2048, types=["experience", "observation", "world"]
)

# Query 2: Cross-vendor pattern query (procedural tactics across SaaS)
pattern_query = (
    f"SaaS software licence negotiation tactics: support-fee unbundling success rate, "
    f"early-renewal discount outcomes, multi-year contract concessions, volume tier discounts, "
    f"quarter-end timing deadline effects, and failed tactics"
)
pattern_results = hindsight_service.recall_memories(
    query=pattern_query, budget="high", max_tokens=2048, types=["experience", "observation", "world"]
)

# Fuse and deduplicate by persistent memory ID
seen_ids = set()
for m in (vendor_results + pattern_results):
    mid = m.get("id")
    if mid and mid not in seen_ids:
        seen_ids.add(mid)
        recalled_memories.append(m)
```

---

## 3. The Before / After Story: Empirical Evidence

During the evaluation run over the held-out deals, we observed distinct qualitative and quantitative divergence between Memory OFF and Memory ON:

### Case Study: Deal `held-001` (TracePeak Cloud Monitoring)
- **Initial Quote**: $3,050,000 (450 hosts, enterprise tier, 18% support fee, Q2 renewal).
- **Actual Historical Settlement Price**: $2,759,140 (approx 9.5% net concession).

#### Without Memory (Memory OFF):
- **Target Price**: $2,512,400 (Aggressive generic 17.6% cut).
- **Error vs Actual**: 8.94%.
- **Tactics**: Standard generic textbook playbook ("Ask for 15% discount", "Threaten to evaluate competitors", "Offer multi-year agreement").
- **Flaw**: Completely unaware that TracePeak sales representatives have hard compensation floors prohibiting list discounts exceeding 10%, but have full discretion to unbundle line-item telemetry and waive support fees.

#### With Persistent Memory (Memory ON):
- **Target Price**: $2,650,000.
- **Error vs Actual**: **3.96%** (a **55.77% error reduction**).
- **Citations**: Cites memory `e626e14c-12b7-4c48-8dfa-80bb7efce182`.
- **Tactical Realignment**:
  - Highlights TracePeak's specific habit of bundling an 18% unmonitored telemetry audit.
  - Specifically prescribes demanding an unbundled telemetry line-item review before quarter close.
  - Accurately anticipates the vendor's standard objection ("Volume tiers are fixed") and prepares the counter-move.

---

## 4. What Broke During Development & How We Resolved It

| Component | Failure Encountered | Root Cause | Engineering Solution |
| :--- | :--- | :--- | :--- |
| **Python on Windows** | `UnicodeEncodeError: 'charmap' codec can't encode character '\u2011'` | Windows default console encoding is `cp1252`, which fails on non-breaking hyphens and currency symbols in LLM JSON output. | Added `sys.stdout.reconfigure(encoding='utf-8')` to entrypoints and CLI runners. |
| **Groq Inference** | `429 RateLimitError: TPM/TPD limit exceeded` on free tier | `openai/gpt-oss-120b` has an 8k TPM cap; deep reasoning tokens quickly hit daily limits. | Switched to `qwen/qwen3.8-27b`, capped `max_tokens=650`, prioritized numeric JSON keys at top of schema, and added graceful fallback pricing algorithms. |
| **Hindsight Idempotency** | Duplicate memory creation on test re-runs | Naive sequential retention creates new document records for every execution. | Implemented Hindsight's native `document_id` parameter (`dealmemory-negotiation-{deal_id}`), ensuring deterministic upserts. |
| **UI Screenshot Driver** | Subagent Playwright CDN returned HTTP 404 | Upstream azureedge CDN outage for win32_x64 driver v1.57.0. | Implemented automated headless Microsoft Edge CLI pipeline (`--headless=new`, `--screenshot`, `--virtual-time-budget=3000`) for pixel-perfect screenshot captures. |

---

## 5. Lessons Learned About Using Hindsight

1. **Document Upsert is Essential for Reproducibility**: Using deterministic `document_id` values ensures test runs and database reseeding do not create duplicate memory nodes or pollute semantic recall rankings.
2. **Recall Budget Matters**: Setting `budget="high"` on complex semantic queries significantly improves multi-hop association, surfacing cross-vendor patterns that low-budget queries miss.
3. **Structured Context Outperforms Raw Text**: Formatting retained content with clear sections (`[DEAL PROFILE]`, `[TACTICS ATTEMPTED]`, `[LESSONS LEARNED]`) produces much cleaner semantic extraction in Hindsight's graph representation than free-form narrative paragraphs.
4. **Decoupling Evidence from Reasoning**: Retaining the principle that the memory system provides *facts* and the LLM provides *reasoning* keeps hallucinations strictly bounded and auditable.
