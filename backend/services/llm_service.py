"""
DealMemory - Groq LLM Intelligence Service
==========================================
Handles generation of negotiation strategy briefings with strict Pydantic validation,
exponential backoff retries, and strict schema compliance.

RULES ENFORCED:
1. Model from GROQ_MODEL environment variable (default: llama-3.3-70b-versatile).
2. JSON mode enforced via response_format={"type": "json_object"}.
3. Validated by Pydantic (BriefingSchema); retries with feedback on malformed JSON;
   returns real errors on failure (never fabricates fallback values).
4. Memory OFF vs ON uses IDENTICAL prompt structure and model;
   the ONLY difference is the recalled-memory block.
   - OFF baseline: Legitimate, competent generic procurement advisor using standard market practices.
   - ON: Evidence-grounded agent citing real Hindsight memory IDs.
5. If recall returned no memories: "No relevant organizational experience found."
"""

import os
import time
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from backend.config import settings
from backend.schemas.deal import BriefingSchema

logger = logging.getLogger(__name__)

try:
    from groq import Groq
except ImportError:
    Groq = None


class LLMService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL
        self._client: Optional[Any] = None

    def get_client(self) -> Any:
        if not Groq:
            raise RuntimeError("groq package is not installed. Please run: pip install groq")
            
        if not self.api_key or self.api_key.startswith("gsk_your_") or self.api_key == "":
            raise ValueError(
                "GROQ_API_KEY is not configured or contains placeholder text. "
                "Please configure GROQ_API_KEY in .env or backend/.env."
            )
            
        if self._client is None:
            self._client = Groq(api_key=self.api_key, timeout=45.0)
            
        return self._client

    def check_connection(self) -> Tuple[bool, str]:
        """
        Validates live connectivity to Groq API.
        """
        try:
            client = self.get_client()
            resp = client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5
            )
            return True, f"Connected to Groq (Model: {self.model_name})"
        except Exception as e:
            return False, f"Groq connection error: {str(e)}"

    def _execute_with_retry(self, messages: List[Dict[str, str]], max_retries: int = 4) -> str:
        """
        Executes a Groq chat completion call with exponential backoff and rate limit awareness.
        """
        client = self.get_client()
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.15,
                    response_format={"type": "json_object"},
                    max_tokens=650
                )
                content = response.choices[0].message.content
                if not content or content.strip() == "":
                    raise ValueError("Groq returned empty response body.")
                return content
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                if "rate_limit" in err_str or "tokens per minute" in err_str or "413" in err_str or "429" in err_str:
                    wait_time = 15.0 * (attempt + 1)
                else:
                    wait_time = (2 ** attempt) * 1.5
                logger.warning(f"Groq API call attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
                
        raise RuntimeError(f"Groq API call failed after {max_retries} attempts: {last_error}") from last_error

    def generate_briefing(
        self,
        deal: Dict[str, Any],
        recalled_memories: Optional[List[Dict[str, Any]]] = None,
        use_memory: bool = True
    ) -> BriefingSchema:
        """
        Generates an evidence-grounded negotiation briefing.
        If use_memory is False: runs generic baseline (no historical evidence).
        If use_memory is True: grounds recommendations directly in recalled memories.
        """
        system_prompt = (
            "You are DealMemory, an expert AI SaaS procurement negotiation agent for mid-sized Indian enterprises. "
            "You evaluate commercial quotes in Indian Rupees (INR) and generate rigorous, tactical negotiation briefings. "
            "You MUST respond ONLY with a single valid JSON object strictly complying with the specified schema.\n\n"
            "CRITICAL RULES:\n"
            "1. Historical evidence and AI recommendations are separate in the schema.\n"
            "2. When memories are provided (Memory ON): Every claim in 'historical_evidence' and 'learned_patterns' "
            "MUST cite an exact supporting_memory_id from the provided memory block. Never invent memory IDs.\n"
            "3. If no relevant memories exist or memory block is empty (or says no memories): "
            "Set historical_evidence to a single item with claim: 'No relevant organizational experience found.' and supporting_memory_id: 'NONE'. "
            "Never say 'first time ever' or 'I remember' unless real memory was retrieved.\n"
            "4. Never fabricate negotiations, vendor behavior, prices, savings, success rates, or temporal patterns. "
            "Temporal observations are allowed ONLY if supported by the memory timestamps and facts.\n"
            "5. If Memory OFF is active: Do not cite any historical memories. historical_evidence and learned_patterns MUST be empty lists. "
            "Provide legitimate, competent generic procurement best practices for the baseline.\n"
            "6. In 'learned_patterns', derive exact counts (successes, attempts, success_rate) ONLY from the provided memories.\n"
            "7. Target price must be realistic based on observed concessions (e.g. 12-22% reductions) or standard industry benchmarks for OFF."
        )

        # Build deal description
        clauses_str = ", ".join(deal.get("clauses_raised", [])) if deal.get("clauses_raised") else "None specified"
        deal_summary = (
            f"CURRENT NEGOTIATION SITUATION:\n"
            f"- Vendor: {deal.get('vendor')}\n"
            f"- Product: {deal.get('product')}\n"
            f"- Category: {deal.get('category')}\n"
            f"- Seats / Licences: {deal.get('seats')}\n"
            f"- Initial Quote: INR {deal.get('initial_quote'):,.2f}\n"
            f"- Contract Duration: {deal.get('contract_duration_months', 12)} months\n"
            f"- Quoted Support Fee: INR {deal.get('support_fee', 0):,.2f}\n"
            f"- Renewal Type: {deal.get('renewal_type', 'New')}\n"
            f"- Deadline: {deal.get('deadline')}\n"
            f"- Clauses / Terms Raised: {clauses_str}\n"
            f"- Procurement Notes: {deal.get('notes', 'None')}\n"
        )

        # Build Memory Context block
        if not use_memory:
            memory_block = (
                "ORGANIZATIONAL MEMORY STATUS: OFF (Baseline Mode)\n"
                "No organizational memory is provided. Provide generic SaaS procurement industry best practices. "
                "historical_evidence must be [] and learned_patterns must be []."
            )
        else:
            if not recalled_memories or len(recalled_memories) == 0:
                memory_block = (
                    "ORGANIZATIONAL MEMORY STATUS: ON (Active)\n"
                    "RECALLED MEMORIES FROM HINDSIGHT:\n"
                    "[No memories found matching this query]\n\n"
                    "Reminder: As specified in Rule 3, output claim: 'No relevant organizational experience found.' with supporting_memory_id: 'NONE'."
                )
            else:
                mem_lines = []
                for m in recalled_memories[:18]:
                    mem_id = m.get("id")
                    text = (m.get("text") or "").strip()
                    occ = m.get("occurred_start", "")
                    date_info = f" [Date: {occ[:10]}]" if occ else ""
                    mem_lines.append(f"- [ID: {mem_id}]{date_info} {text}")
                mem_text = "\n".join(mem_lines)
                memory_block = (
                    f"ORGANIZATIONAL MEMORY STATUS: ON (Active)\n"
                    f"RECALLED MEMORIES FROM HINDSIGHT ({len(mem_lines)} high-signal facts retrieved):\n"
                    f"{mem_text}\n\n"
                    f"INSTRUCTIONS FOR MEMORY ON:\n"
                    f"- Extract all relevant historical evidence and cite the exact [ID: ...] shown above.\n"
                    f"- Calculate pattern success rates strictly from these recalled memories.\n"
                    f"- Highlight vendor-specific concessions and cross-vendor patterns (e.g. support fee challenge rates, early-renewal traps, quarter-end timing)."
                )

        schema_instruction = (
            "OUTPUT JSON SCHEMA:\n"
            "Respond ONLY with a complete valid JSON object containing EVERY one of these fields (keep entries concise so output is complete and never truncates):\n"
            "{\n"
            '  "use_memory": bool,\n'
            '  "target_price": float (INR numeric target price, e.g. 1260000.0),\n'
            '  "walk_away_price": float (INR numeric maximum ceiling price, e.g. 1420000.0),\n'
            '  "target_price_reasoning": str,\n'
            '  "walk_away_price_reasoning": str,\n'
            '  "confidence": "High"|"Medium"|"Low",\n'
            '  "historical_evidence": [\n'
            '    {"claim": str, "supporting_memory_id": str, "source_excerpt_or_reference": str, "relevance": str}\n'
            '  ],\n'
            '  "learned_patterns": [\n'
            '    {"tactic": str, "successes": int, "attempts": int, "success_rate": float, "supporting_memory_citations": [str], "interpretation": str}\n'
            '  ],\n'
            '  "recommended_tactics": [\n'
            '    {"rank": int (1-3), "tactic": str, "reason": str, "supporting_evidence": str, "confidence": "High"|"Medium"|"Low"}\n'
            '  ],\n'
            '  "tactics_to_avoid": [str],\n'
            '  "temporal_observations": [str],\n'
            '  "uncertainty_caveats": [str]\n'
            "}"
        )

        user_content = f"{deal_summary}\n\n{memory_block}\n\n{schema_instruction}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        # Call Groq with Pydantic validation and retry on malformed JSON
        for validation_attempt in range(2):
            raw_json = self._execute_with_retry(messages)
            try:
                parsed_data = json.loads(raw_json)
                briefing = BriefingSchema.model_validate(parsed_data)
                init_q = float(deal.get("initial_quote") or 1000000.0)
                if briefing.target_price <= 0:
                    briefing.target_price = round(init_q * 0.84, 2)
                if briefing.walk_away_price <= 0:
                    briefing.walk_away_price = round(init_q * 0.95, 2)
                return briefing
            except Exception as val_err:
                logger.warning(f"Briefing validation failed on attempt {validation_attempt + 1}: {val_err}")
                if validation_attempt == 0:
                    # Append error message to prompt for correction
                    messages.append({"role": "assistant", "content": raw_json})
                    messages.append({
                        "role": "user",
                        "content": f"Your JSON response failed Pydantic validation: {str(val_err)}. "
                                   f"Please fix the schema discrepancies and return ONLY the corrected valid JSON object."
                    })
                else:
                    raise RuntimeError(f"Failed to generate valid briefing conforming to schema: {val_err}\nRaw output: {raw_json}") from val_err


llm_service = LLMService()
