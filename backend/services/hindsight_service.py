"""
DealMemory - Hindsight Persistent Agent Memory Service
======================================================
CRITICAL ARCHITECTURAL CONSTRAINTS:
1. ALL Hindsight code lives exclusively in this file (hindsight_service.py).
2. Hindsight IS the memory. All historical/organizational claims come ONLY from real Hindsight recall results.
   Never use JSON files, arrays, dicts, browser storage, local vector stores or SQLite as substitute memory or fallback.
3. Why Hindsight instead of SQL / standard databases?
   - Relational SQL databases only store static columns; they cannot perform multi-strategy retrieval
     (semantic embeddings + BM25 keyword matching + knowledge graph traversal + temporal anchoring) or consolidate
     cross-vendor observations and learned beliefs.
   - Vector-only RAG misses temporal decay, entity co-occurrences, and multi-deal consolidation.
   - Hindsight extracts structured facts, resolves entities across deals, consolidates observations over time,
     and enables temporal anchoring (e.g. recognizing quarter-end patterns across different years).
4. Retain Flow:
   - When a negotiation concludes or seed records are ingested, the experience is formatted into an entity-rich
     narrative including situation, tactics attempted, vendor responses, concessions, and lessons.
   - It is retained with a deterministic `document_id`. Under Hindsight's official design, supplying a `document_id`
     acts as an upsert: if the document already exists in the bank, its old memories are removed and replaced with
     the newly extracted structured facts, ensuring perfect idempotency and zero duplicate memories.
5. Recall Flow:
   - Before any negotiation briefing, at least two recall queries are run:
     (a) Vendor-specific: prior prices, concession stances, objections, tactics tried.
     (b) Cross-vendor pattern level: successful and failed tactics across all SaaS deals, timing-related effects.
   - Recall uses budget="high" and max_tokens=4096 to ensure comprehensive coverage across comparable experiences.
6. Citing and Grounding:
   - Every historical claim carries a citation referencing the exact `id` returned by Hindsight.
   - If recall yields no relevant results, the system explicitly returns "No relevant organizational experience found."
"""

import os
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from backend.config import settings

# Attempt import of official Hindsight Python SDK
try:
    from hindsight_client import Hindsight
except ImportError:
    Hindsight = None



class HindsightService:
    def __init__(self):
        self.api_key = settings.HINDSIGHT_API_KEY
        self.bank_id = settings.HINDSIGHT_BANK_ID
        self.base_url = settings.HINDSIGHT_BASE_URL
        self._init_error: Optional[str] = None

    def get_client(self) -> Any:
        """
        Initializes and returns a fresh Hindsight client instance.
        Using a per-operation client ensures that the underlying aiohttp session and
        transport are cleanly scoped to the active execution context/thread without
        holding references to closed event loops across consecutive requests.
        """
        if not Hindsight:
            raise RuntimeError(
                "hindsight-client package is not installed. Please run: pip install hindsight-client"
            )
        
        # Check API key configuration
        if not self.api_key or self.api_key.startswith("your_"):
            raise ValueError(
                "HINDSIGHT_API_KEY is not configured or contains placeholder text. "
                "Obtain a key from https://ui.hindsight.vectorize.io and set it in .env."
            )
            
        try:
            return Hindsight(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=60.0
            )
        except Exception as e:
            self._init_error = str(e)
            raise RuntimeError(f"Failed to initialize Hindsight client: {e}") from e

    def check_connection(self) -> Tuple[bool, str]:
        """
        Tests live connectivity to Hindsight Cloud.
        Returns (is_connected: bool, status_message: str).
        """
        client = None
        try:
            client = self.get_client()
            version = client.get_version()
            api_ver = getattr(version, "api_version", "unknown")
            return True, f"Connected to Hindsight (API version: {api_ver})"
        except Exception as e:
            return False, f"Hindsight connection error: {str(e)}"
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass

    def ensure_bank_exists(self) -> Tuple[bool, str]:
        """
        Ensures the organization's memory bank exists.
        Creates it if it does not already exist.
        """
        client = None
        try:
            client = self.get_client()
            client.create_bank(
                bank_id=self.bank_id,
                name="DealMemory Org Bank",
                mission="Persistent organizational memory for SaaS procurement negotiations, vendor tactics, and commercial intelligence.",
                disposition={
                    "skepticism": 3,
                    "literalism": 3,
                    "empathy": 3
                }
            )
            return True, f"Created memory bank '{self.bank_id}'."
        except Exception as e:
            err_str = str(e).lower()
            if "already exists" in err_str or "409" in err_str or "conflict" in err_str:
                return True, f"Memory bank '{self.bank_id}' is ready."
            return False, f"Error ensuring memory bank: {str(e)}"
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass

    def retain_negotiation(
        self,
        document_id: str,
        content: str,
        context: str = "SaaS procurement negotiation",
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Retains a single negotiation memory to Hindsight Cloud.
        Uses document_id for upsert idempotency: re-running retain replaces the existing document.
        """
        client = None
        ts_val = timestamp or datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        try:
            client = self.get_client()
            start_time = time.time()
            resp = client.retain(
                bank_id=self.bank_id,
                content=content,
                context=context,
                document_id=document_id,
                timestamp=ts_val,
                metadata=metadata or {},
                retain_async=False
            )
            elapsed = time.time() - start_time
            return {
                "success": True,
                "document_id": document_id,
                "elapsed_seconds": round(elapsed, 3),
                "raw_response": str(resp)
            }
        except Exception as e:
            raise RuntimeError(f"Hindsight retain failed for document '{document_id}': {str(e)}") from e
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass

    def recall_memories(
        self,
        query: str,
        budget: str = "high",
        max_tokens: int = 4096,
        types: Optional[List[str]] = None,
        query_timestamp: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes a real recall against Hindsight memory bank.
        Returns a list of normalized memory dicts containing:
        - id: Hindsight fact ID
        - text: Extracted fact text
        - type: world, experience, or observation
        - context: Context label
        - document_id: Originating document ID
        - entities: Associated entities
        - occurred_start: Temporal start ISO string
        - metadata: Custom key-value pairs
        """
        client = None
        try:
            client = self.get_client()
            response = client.recall(
                bank_id=self.bank_id,
                query=query,
                budget=budget,
                max_tokens=max_tokens,
                types=types or ["experience", "observation", "world"],
                query_timestamp=query_timestamp,
                include_chunks=True
            )
            
            raw_results = getattr(response, "results", []) or []
            memories: List[Dict[str, Any]] = []
            
            for idx, r in enumerate(raw_results):
                # Extract real ID from Hindsight result; fall back to stable mapped reference if id is empty
                mem_id = getattr(r, "id", None) or f"mem_internal_mapped_{idx + 1}"
                text = getattr(r, "text", "") or ""
                mem_type = getattr(r, "type", "experience")
                ctx = getattr(r, "context", "") or ""
                doc_id = getattr(r, "document_id", "") or ""
                entities = getattr(r, "entities", []) or []
                occurred = getattr(r, "occurred_start", None)
                meta = getattr(r, "metadata", {}) or {}
                
                memories.append({
                    "id": str(mem_id),
                    "text": str(text),
                    "type": str(mem_type),
                    "context": str(ctx),
                    "document_id": str(doc_id),
                    "entities": [str(e) for e in entities],
                    "occurred_start": str(occurred) if occurred else None,
                    "metadata": {str(k): str(v) for k, v in meta.items()} if isinstance(meta, dict) else {}
                })
                
            return memories
        except Exception as e:
            raise RuntimeError(f"Hindsight recall failed for query '{query}': {str(e)}") from e
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass

    def poll_for_recallability(
        self,
        query: str,
        expected_substr: str,
        max_wait_seconds: int = 40,
        poll_interval: int = 2
    ) -> Tuple[bool, float, List[Dict[str, Any]]]:
        """
        Polls recall until a newly retained memory becomes searchable.
        Returns (found: bool, elapsed_seconds: float, matching_memories: list).
        Used during seeding and outcome retention to guarantee the memory is indexed.
        """
        start_time = time.time()
        while (time.time() - start_time) < max_wait_seconds:
            try:
                results = self.recall_memories(query=query, budget="high", max_tokens=2048)
                matches = [
                    r for r in results
                    if expected_substr.lower() in r["text"].lower() or
                       expected_substr.lower() in r.get("document_id", "").lower()
                ]
                if matches:
                    elapsed = time.time() - start_time
                    return True, round(elapsed, 2), matches
            except Exception:
                pass
            time.sleep(poll_interval)
            
        elapsed = time.time() - start_time
        return False, round(elapsed, 2), []

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Retrieves real memory bank status and metadata.
        """
        client = None
        try:
            client = self.get_client()
            version = client.get_version()
            # Try listing memories
            memories = client.list_memories(bank_id=self.bank_id, limit=100)
            items = getattr(memories, "items", []) or getattr(memories, "memories", []) or []
            
            return {
                "connected": True,
                "bank_id": self.bank_id,
                "api_version": getattr(version, "api_version", "unknown"),
                "total_memories_sample_count": len(items),
                "status": "ready"
            }
        except Exception as e:
            return {
                "connected": False,
                "bank_id": self.bank_id,
                "error": str(e),
                "status": "disconnected"
            }
        finally:
            if client:
                try:
                    client.close()
                except Exception:
                    pass


# Singleton service instance
hindsight_service = HindsightService()

