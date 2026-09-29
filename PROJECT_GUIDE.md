# DealMemory — Project Guide

## What is DealMemory?

Imagine you run an organization that buys a lot of software: CRMs, cybersecurity tools, cloud monitoring, and HR platforms. Every time a contract comes up for renewal, a sales representative tries to charge you high prices, push expensive support add-ons, or lock you into multi-year commitments. 

Usually, the person doing the negotiation is at a huge disadvantage. Why? Because the vendor’s sales team negotiates these contracts all day long, while your team might only negotiate with that specific vendor once a year. Worse, if the person who negotiated last year’s contract left your company, all their knowledge left with them. Nobody remembers that the vendor was willing to drop their 18% support fee on the last day of September, or that threatening to switch to a competitor caused them to offer a 20% discount.

**DealMemory solves this problem.** It is an AI copilot for software contract negotiations that has a real, permanent "organizational memory." Every time your company negotiates a deal, DealMemory remembers what happened: what tactics were tried, how the vendor responded, what price was agreed on, and what lessons were learned.

The next time anyone on your team prepares to negotiate, DealMemory searches that organizational memory, finds relevant past experiences, and tells you: *"Here is what happened with this vendor before, here is the exact counter-offer you should make, and here are the tactics that actually worked."*

### The Core Idea

```
Situation
  ↓
Tactic Attempted
  ↓
Vendor Response
  ↓
Outcome (Agreed Price & Terms)
  ↓
Lesson Learned
  ↓
Retained into Hindsight Memory Bank
  ↓
Future Recall on Next Deal
  ↓
Smarter Counter-Offer & Strategy
```

### Why DealMemory is NOT Just a Chatbot, Database, or Deal Log

| Tool Type | What It Does | Why DealMemory is Fundamentally Different |
| :--- | :--- | :--- |
| **A Standard Chatbot (e.g., generic ChatGPT)** | Starts from zero on every conversation. It gives textbook advice (*"Ask for a 10% discount"*), has no idea what your company paid before, and cannot remember what happened yesterday. | DealMemory doesn't guess. It searches a real, permanent cloud memory bank of your actual past deals before answering, citing exact historical records. |
| **A Normal Database (e.g., SQL / Postgres / Airtable)** | Stores rows and columns (e.g., date, vendor name, dollar amount). You can filter or sort by vendor, but a SQL database cannot understand abstract concepts like *"concession habits"*, *"vendor panic at quarter-end"*, or cross-vendor patterns. | DealMemory uses **Hindsight Cloud**, which extracts semantic facts, connects related entities across deals, and understands relationships over time. |
| **A Searchable Deal Log (e.g., Notion or Google Docs)** | A pile of meeting notes and contracts. A human has to read through pages of old notes to find anything useful, which rarely happens before a fast-moving phone call. | DealMemory autonomously performs deep semantic retrieval and fuses past facts directly into an executable negotiation briefing in seconds. |

---

## 1. What the Application Does

Here is the complete journey of how a procurement team uses DealMemory:

1. **A buyer enters a new deal context**: You receive an initial price quote from a software vendor (e.g., NimbusCRM quotes $185,000 for 450 seats with a 20% mandatory support fee).
2. **DealMemory searches organizational memory**: DealMemory sends queries to **Hindsight Cloud**, searching for past negotiations with that specific vendor and similar tactics across all software deals.
3. **Hindsight returns verified historical evidence**: Hindsight finds relevant past deal facts, complete with permanent Memory IDs and timestamps (e.g., *"NimbusCRM previously waived its support fee when offered an annual prepayment"*).
4. **The AI reasons over the retrieved facts**: DealMemory feeds both the current deal terms and the retrieved historical facts to an AI reasoning model (Groq).
5. **DealMemory generates a dual briefing**: You see a side-by-side view:
   - **Memory OFF (Baseline)**: What a generic AI would recommend with zero organizational memory.
   - **Memory ON (Grounded)**: An evidence-backed counter-offer, target price, ceiling walk-away price, recommended tactics, and explicit citations to previous deals.
6. **You conduct the negotiation**: Armed with the briefing, your team negotiates with the vendor knowing their historical boundaries.
7. **You record what happened**: When the deal closes, you enter the final price, which tactics worked, which failed, and the key lesson learned.
8. **DealMemory permanently retains the outcome**: This new outcome is saved directly into Hindsight Cloud.
9. **Future deals become immediately smarter**: The next negotiation for any team member will instantly recall this new outcome.

---

## 2. The Main Pages in DealMemory

The application contains five main pages accessible via the top navigation bar:

### Page 1: Dashboard (`/`)
- **What it is for**: The central command center showing an executive overview of all software procurement activities.
- **What you see**:
  - Live System Health indicator showing the real-time status of SQLite, Hindsight Cloud, and Groq.
  - KPI metric cards: Total Tracked Negotiations, Identified Cost Savings, and Retained Memory Units in Hindsight.
  - Quick action buttons to launch briefings or record deal outcomes.
  - A table of recent negotiations with vendor names, categories, initial quotes, and analysis statuses.
- **Behind the scenes**: Loads deal records from SQLite and fetches live memory statistics from Hindsight Cloud.

### Page 2: Negotiations & Dual Briefing (`/negotiations`)
- **What it is for**: Creating new deals and running the dual-mode AI negotiation briefing.
- **What you see**:
  - A deal selector and a button to register new negotiations.
  - Two briefing buttons: **"Analyze Without Hindsight (Memory OFF)"** and **"Analyze With Hindsight (Memory ON)"**.
  - A side-by-side card layout showing target prices, walk-away prices, and tactical advice.
  - Under Memory ON, a dedicated **"Grounded Historical Evidence"** section showing exact claims and clickable Hindsight Memory IDs.
  - A **"Record Deal Outcome"** button that lets you input what actually happened after negotiating.
- **Behind the scenes**: Memory OFF calls Groq directly. Memory ON queries Hindsight Cloud twice (vendor query + pattern query), fuses the results, and passes them to Groq with strict Pydantic JSON validation.

### Page 3: Record Outcome (`/outcome`)
- **What it is for**: Closing the feedback loop after a negotiation finishes.
- **What you see**:
  - Form fields for: Final Agreed Price, Contract Duration, Tactics Attempted (with vendor reaction and success checkbox), Stance Summary, Terms Accepted vs Rejected, and Lessons Learned.
  - A prominent button: **"Save Outcome & Retain into Hindsight"**.
- **Behind the scenes**: Saves the outcome to SQLite for audit and sends the structured narrative to Hindsight Cloud using a deterministic `document_id`.

### Page 4: Organizational Memory & Intelligence Explorer (`/memory`)
- **What it is for**: Directly exploring and testing what your company's memory bank knows.
- **What you see**:
  - Memory Bank metrics: Connection status, API version, and total documents retained.
  - **"Test Organizational Memory (Live Hindsight Recall)"**: A live search box with a Budget selector (Low, Mid, High Deep Recall), preset example questions, and an **"Execute Recall"** button.
  - **"Recalled Memory Facts"**: Real-time cards displaying every fact retrieved from Hindsight Cloud, including Fact IDs, full fact text, and source document links.
  - **"Vendor Concession Profiles"**: Cards summarizing historical patterns for each vendor.
- **Behind the scenes**: Calls `POST /api/memory/recall` which connects live to Hindsight Cloud's multi-strategy retrieval engine.

### Page 5: Interactive Demo & Empirical Evaluation (`/demo`)
- **What it is for**: Experiencing a guided 5-step walkthrough and reviewing empirical benchmark results.
- **What you see**:
  - A 5-step visual walkthrough demonstrating the closed loop: Seed Memory → Memory OFF Briefing → Memory ON Briefing → Retain Outcome → Verify Future Recall.
  - An **"Empirical Benchmark Evaluation"** section showing measured accuracy numbers on held-out test deals.
  - A **"Run Sequential Evaluation"** button that re-runs the benchmark live.
  - A chronological learning curve table showing how error rates decreased as the memory bank grew.
- **Behind the scenes**: Evaluates held-out deals in strict chronological order and calculates target price error against ground truth.

---

## 3. How the AI Part Works

DealMemory uses a clean division of labor between memory and reasoning:

```
+--------------------------------------------------------------------------+
|  HINDSIGHT CLOUD                                                         |
|  = The Organizational Memory (Stores verified facts, dates, concessions) |
+--------------------------------------------------------------------------+
                                     ↓ (Provides Historical Evidence)
+--------------------------------------------------------------------------+
|  GROQ API (qwen/qwen3.8-27b)                                             |
|  = The Reasoning Engine (Analyzes the deal and formulates tactics)       |
+--------------------------------------------------------------------------+
                                     ↓ (Outputs Structured JSON Briefing)
+--------------------------------------------------------------------------+
|  FASTAPI BACKEND & REACT FRONTEND                                        |
|  = The Presentation Layer (Displays evidence, citations, and numbers)    |
+--------------------------------------------------------------------------+
```

### Why AI Must Never Invent Historical Facts
Language models are notorious for "hallucinating"—confidently inventing convincing details that never happened. In procurement, hallucinating a vendor discount could cost an organization hundreds of thousands of dollars.

DealMemory prevents this through strict rules:
1. **The LLM is forbidden from inventing historical evidence**: It can only cite memories that Hindsight actually returned.
2. **Every historical claim carries a citation**: Each claim displays the exact UUID memory ID from Hindsight.
3. **If Hindsight finds nothing**, the AI is required to state: *"No relevant organizational experience found."*

---

## 4. How Hindsight Works

**Hindsight** is a specialized persistent memory cloud service built for AI agents.

### Retain vs. Recall
- **RETAIN ("Learn this experience")**: When a deal concludes, DealMemory packages the negotiation story into a structured document and sends it to Hindsight. Hindsight extracts key entities (vendor names, prices, percentages, dates) and weaves them into its knowledge graph.
- **RECALL ("Find relevant previous experience")**: When a new deal begins, DealMemory asks Hindsight semantic questions. Hindsight uses a 4-way retrieval pipeline (vector embeddings, BM25 keyword matching, knowledge graph traversal, and temporal recency) to surface the most relevant facts.

### Key Concepts
- **Organizational Memory**: Knowledge belongs to the company, not individual employees. Even if your entire procurement team changes, new hires instantly possess the collective memory of every previous deal.
- **Cross-Vendor Learning**: Some tactics work across multiple vendors. For example, learning that software companies concede discounts in the final two weeks of their fiscal quarter benefits every deal.
- **Failure Memory**: Remembering what *didn't* work is often more valuable than remembering what worked. DealMemory flags tactics that backfired so you avoid repeating mistakes.

---

## 5. How the Live Recall Feature Works

On the **Organizational Memory** page (`/memory`), you can interact directly with Hindsight Cloud:

```
You enter a query (e.g., "NimbusCRM renewal discount tactics")
  ↓
Frontend sends HTTP POST to /api/memory/recall
  ↓
FastAPI backend calls hindsight_service.recall_memories()
  ↓
Hindsight Cloud searches the persistent memory bank
  ↓
Hindsight returns structured facts, confidence scores, and Memory IDs
  ↓
Backend formats the response into JSON
  ↓
Frontend renders individual fact cards showing Fact ID, Text, Context, and Source
```

### What the Settings Mean
- **Budget: High (Deep Recall)**: Tells Hindsight to perform a comprehensive, multi-hop search across graph relations and raw text.
- **Recalled Memory Facts**: The specific, verified sentences extracted by Hindsight from past contracts and debrief notes.
- **Fact ID**: The permanent UUID assigned by Hindsight to that discrete piece of information.

---

## 6. How the Backend Works

The backend is built in **Python 3.12** using **FastAPI**:
- **FastAPI**: Modern, high-performance web framework providing automated Swagger documentation at `http://localhost:8000/docs`.
- **Pydantic v2**: Validates all incoming and outgoing data, guaranteeing that the AI's responses strictly match the expected JSON structure.
- **Hindsight Client SDK (`hindsight-client`)**: Communicates with Hindsight Cloud for memory retention and retrieval.
- **Groq Python SDK (`groq`)**: Connects to the Groq inference engine to run `qwen/qwen3.8-27b` with ultra-low latency.
- **SQLite Database (`dealmemory.db`)**: Stores local deal status, UI history, and benchmark ground truth. *SQLite is strictly barred from serving as memory to the AI.*

---

## 7. How the Frontend Works

The frontend is a single-page application built with **React 18**, **TypeScript**, and **Tailwind CSS**:
- **React + Vite**: Delivers instant hot-module reloading and fast production builds.
- **Tailwind CSS**: Sleek dark-mode aesthetic with custom slate and sky color palettes.
- **Lucide React**: Clean icons throughout the interface.
- **Frontend-to-Backend Flow**: The UI interacts with the backend strictly through HTTP REST calls defined in `frontend/src/services/api.ts`. No secret API keys exist in the frontend.

---

## 8. Important Files in the Project

| File / Folder | What It Does |
| :--- | :--- |
| `backend/main.py` | FastAPI application entry point; sets up CORS and mounts routes. |
| `backend/config.py` | Loads and validates configuration from `.env`. |
| `backend/database.py` | Initializes SQLite tables for deals, outcomes, briefings, and demo state. |
| `backend/services/hindsight_service.py` | **The sole Hindsight integration file.** Handles client creation, retain, recall, and bank health checks. |
| `backend/services/llm_service.py` | Connects to Groq; manages prompts, Pydantic JSON mode, and fallback calculations. |
| `backend/services/negotiation_service.py` | Orchestrates the briefing generation, 2-query memory fusion, and outcome retention loop. |
| `backend/services/eval_service.py` | Executes the sequential benchmark over held-out deals and compiles learning curves. |
| `backend/routes/` | API route definitions (`health.py`, `negotiations.py`, `memory.py`). |
| `backend/tests/test_api.py` | Automated test suite verifying health checks, negotiations, and consecutive recall requests. |
| `frontend/src/App.tsx` | Main React application layout and navigation tab controller. |
| `frontend/src/pages/` | Page components (`DashboardPage`, `NegotiationPage`, `OutcomePage`, `MemoryPage`, `DemoPage`). |
| `frontend/src/services/api.ts` | Frontend HTTP client functions communicating with the backend. |
| `seed/negotiations.json` | 16 curated SaaS negotiations across 5 vendors. |
| `seed/split.json` | Defines the 12 seed deals and 4 held-out evaluation deals. |
| `scripts/demo_cli.py` | Terminal-based closed-loop demo testing the complete workflow end-to-end. |
| `.env.example` | Template showing required environment variables with placeholders. |
| `run_local.bat` / `run_local.ps1` | One-click local startup scripts for Windows. |

---

## 9. Data Flow Diagrams

### Flow 1: New Negotiation Briefing

```
User (Browser)
  │ (Clicks "Analyze With Hindsight")
  ▼
FastAPI Server (POST /api/negotiations/{id}/analyze)
  │
  ├──► Query 1: Hindsight Recall (Vendor-specific concessions)
  │      ◄── Returns prior quotes & objection stances
  │
  ├──► Query 2: Hindsight Recall (Cross-vendor tactical patterns)
  │      ◄── Returns support unbundling & timing effects
  │
  ├──► Groq LLM (Synthesizes deal params + recalled evidence)
  │      ◄── Returns validated BriefingSchema JSON
  │
  ▼
Frontend UI displays target price, tactics, and evidence citations
```

### Flow 2: Recording Deal Outcome

```
User (Browser)
  │ (Fills outcome form & clicks "Save Outcome & Retain")
  ▼
FastAPI Server (POST /api/negotiations/{id}/outcome)
  │
  ├──► SQLite (Saves record for UI history & audit)
  │
  └──► Hindsight Cloud (client.retain with deterministic doc_id)
         │
         ▼
Hindsight extracts new entities, relationships, and temporal facts
  │
  ▼
Immediately searchable for all future negotiations across the org
```

---

## 10. Memory ON vs. Memory OFF

In the Negotiation Analysis view, DealMemory provides both options side-by-side:

- **Analyze Without Hindsight (Memory OFF)**:
  - Demonstrates how a standard LLM behaves with no access to past experience.
  - Relies on generic rules of thumb (*"Ask for 10% to 15% off"*).
  - Contains **0 historical citations**.
  - Often misses vendor-specific leverage points (like an unbundled support fee).

- **Analyze With Hindsight (Memory ON)**:
  - Retrieves real facts from Hindsight Cloud before generating advice.
  - Cites specific past deals and prices.
  - Pinpoints vendor-specific concession patterns (*"NimbusCRM has a strict 10% list floor, but routinely waives the 18% support fee for 24-month commitments"*).
  - Grounded and auditable.

---

## 11. Empirical Evaluation & Accuracy

DealMemory includes an automated benchmark that measures the real-world value of organizational memory:

> **Label: Results from a small synthetic test set.**  
> *All numbers reflect measured performance on a synthetic test set of 4 held-out SaaS deals evaluated in strict chronological order. No statistical-significance or real-world claims are made.*

### What We Measure
- **Target Price Error**: How close the AI's recommended counter-offer was to the actual final settlement price.
  - **Memory OFF Average Error**: `0.0591` (5.91%)
  - **Memory ON Average Error**: `0.0434` (4.34%)
  - **Net Error Reduction**: **26.5% improvement**
- **Avoided Mistake Rate**: **100.0%** (both modes successfully prevented agreeing to punitive auto-renewal locks or paying above initial list).
- **Learning Curve**: As each held-out deal was completed and retained into Hindsight, the memory bank expanded from 12 to 15 deals, improving pricing accuracy on subsequent negotiations.

---

## 12. Synthetic Data Disclosure

All vendor names (`NimbusCRM`, `TracePeak`, `PeoplePulse`, `ShieldArc`, `TeamNest`) and deal scenarios in the seed dataset are **fictional demonstration data**. They were designed to model realistic enterprise procurement dynamics (annual price escalators, support unbundling, quarter-end urgency, multi-year prepayments), but they do not represent real companies or proprietary commercial contracts.

---

## 13. Environment Variables & Secrets

All configuration is loaded via environment variables in `.env` (or `backend/.env`):

| Variable | Purpose | Is It Secret? | Where It Belongs |
| :--- | :--- | :---: | :--- |
| `HINDSIGHT_API_KEY` | Authentication key for Hindsight Cloud API | **YES** | Backend `.env` only |
| `HINDSIGHT_BANK_ID` | Organization memory bank identifier | No | Backend `.env` |
| `HINDSIGHT_BASE_URL` | Hindsight API server endpoint (`https://api.hindsight.vectorize.io`) | No | Backend `.env` |
| `GROQ_API_KEY` | Authentication key for Groq LLM inference | **YES** | Backend `.env` only |
| `GROQ_MODEL` | LLM model name (e.g., `qwen/qwen3.8-27b`) | No | Backend `.env` |
| `FRONTEND_ORIGIN` | Allowed CORS origin (e.g., `http://localhost:5173`) | No | Backend `.env` |

**Security Note**: API keys are strictly kept on the backend server. The React frontend bundle contains zero secrets.

---

## 14. API Endpoints Reference

| Method | Endpoint | What It Does | When the Frontend Uses It |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Basic system health ping | Health monitors |
| `GET` | `/health/detailed` | Real-time upstream check for Hindsight, Groq, and SQLite | Polled every 20 seconds by the Navbar widget |
| `GET` | `/api/negotiations` | Returns list of all tracked deals | On Dashboard and Negotiations pages |
| `POST` | `/api/negotiations` | Creates a new negotiation deal | When user submits "New Negotiation" form |
| `GET` | `/api/negotiations/{id}` | Fetches full deal details | When viewing a specific negotiation |
| `POST` | `/api/negotiations/{id}/analyze` | Generates dual AI briefing | When user clicks "Analyze" buttons |
| `POST` | `/api/negotiations/{id}/outcome` | Records outcome & retains to Hindsight | When user submits "Record Outcome" form |
| `POST` | `/api/memory/recall` | Executes live semantic search against Hindsight | When user clicks "Execute Recall" on Memory page |
| `GET` | `/api/memory/stats` | Fetches Hindsight bank statistics | On Memory Explorer and Dashboard pages |
| `GET` | `/api/learning/patterns` | Retrieves cross-vendor tactical patterns | On Dashboard and Memory pages |
| `POST` | `/api/demo/seed` | Ingests 12 seed deals into Hindsight | On Demo page or initial setup |
| `POST` | `/api/demo/reset` | Clears local database records | On Demo page "Reset" button |
| `GET` | `/api/demo/status` | Returns seed and connectivity status | On Demo page walkthrough |
| `GET` | `/api/eval/results` | Returns benchmark accuracy and learning curve | On Demo and Evaluation pages |
| `POST` | `/api/eval/run` | Executes sequential evaluation benchmark | When user clicks "Run Sequential Evaluation" |

---

## 15. Error Handling Philosophy

DealMemory follows a strict "no fake data" policy:
- **If Hindsight fails**: The UI displays the real underlying error (e.g., *"Hindsight Memory Status: Unavailable. Reason: ..."*). It never pretends recall succeeded and never generates fake historical memories.
- **If Groq fails**: The user sees the real inference error with actionable guidance.
- **If Recall returns nothing relevant**: The UI explicitly states: *"No relevant organizational experience found."* It never claims memory was retrieved when none existed.
- **If Retain fails**: The deal is saved locally as un-retained, and the UI alerts the user that cloud retention failed.

---

## 16. What You Should Know as the Project Owner

If you forget everything else about this project, remember these 10 things:

1. **Hindsight is the real brain**: The application does not store memories in a local file or SQLite; all memory lives in your real Hindsight Cloud bank.
2. **The LLM is just the voice**: Groq provides the reasoning, but all historical facts come strictly from Hindsight recall.
3. **No hallucinations allowed**: Every historical claim shown in a briefing links to a real Hindsight Memory ID.
4. **The loop actually closes**: When you record an outcome on the Outcome page, it is immediately retained into Hindsight and becomes searchable seconds later.
5. **Memory ON beat Memory OFF by 26.5%**: In benchmark testing, knowing past deals reduced target price error from 5.91% to 4.34%.
6. **Stateless Hindsight Client**: To avoid Python event-loop conflicts, the backend uses clean, per-operation Hindsight clients with automatic session cleanup.
7. **Secrets are safe**: Your API keys live exclusively in your local `.env` file and are never sent to the browser.
8. **One-click startup**: You can launch both servers simultaneously using `run_local.bat` on Windows.
9. **Zero fake fallbacks**: If an external service is down, DealMemory tells you honestly rather than making up answers.
10. **It gets smarter with every deal**: The more software contracts your team negotiates and records, the more leverage your organization accumulates.

---

## 17. How to Run the Project Locally

### 1. Start the Backend
Open a terminal in the project directory:
```powershell
# Activate the Python virtual environment
.\venv\Scripts\activate

# Start the FastAPI server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*API docs will be live at `http://localhost:8000/docs`.*

### 2. Start the Frontend
Open a second terminal in the project directory:
```powershell
cd frontend
npm run dev
```
*Web application will be live at `http://localhost:5173`.*

### 3. One-Click Alternative (Windows)
Double-click `run_local.bat` in the project root to start both servers in separate windows automatically.

### 4. Run the Test Suite
```powershell
python -m pytest backend/tests/test_api.py -v
```

---

## 18. Current Project Status

### Working
- [x] Real Hindsight Cloud bank connectivity, retain, and recall.
- [x] Real Groq LLM inference with Pydantic JSON mode validation.
- [x] Dual-mode negotiation briefing (Memory ON vs. Memory OFF side-by-side).
- [x] Outcome recording with closed-loop retention back to Hindsight Cloud.
- [x] Live Organizational Memory Explorer with query search and preset buttons.
- [x] Empirical evaluation benchmark with 26.5% measured error reduction.
- [x] 8/8 automated tests passing in test suite.
- [x] Production frontend build verified with zero errors and no exposed secrets.

### Fixed in This Task
- **Fixed the "Event loop is closed" error on Live Hindsight Recall**:
  - Identified root cause: A singleton Hindsight client was caching an `aiohttp.ClientSession` bound to an event loop that was prematurely closed by a thread executor wrapper.
  - Implemented clean, stateless per-operation client creation in `HindsightService.get_client()` with reliable `client.close()` cleanup in `finally:` blocks.
  - Tested multiple consecutive recall requests against real Hindsight Cloud (verified 100% success rate with zero closed-loop errors).
  - Enhanced the Memory Explorer UI with instant preset query execution and clear, transparent error reporting.
  - Added an automated regression test (`test_consecutive_recall_endpoint`) to ensure the bug cannot recur.

### Known Limitations
- **Synthetic Seed Data**: Benchmarks are evaluated on 16 synthetic SaaS deals across 5 vendors. Real-world contract evaluation requires continuous human buyer feedback.
- **Free-Tier Rate Limits**: Groq's free-tier has an Output Tokens Per Minute (OTPM) limit. Prompts are kept concise to prevent token cutoffs.
