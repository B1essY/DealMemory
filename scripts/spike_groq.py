"""
DealMemory - Groq Spike Test
Validates:
1. Connection to Groq API
2. Basic chat completion
3. JSON-mode chat completion validated by Pydantic
4. Error handling and timeout configuration
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load .env
root_dir = Path(__file__).resolve().parent.parent
load_dotenv(root_dir / ".env")
load_dotenv(root_dir / "backend" / ".env")

api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not api_key or api_key.startswith("gsk_your_") or api_key == "":
    print("ERROR: GROQ_API_KEY is not set or contains placeholder value.", file=sys.stderr)
    print("Please set GROQ_API_KEY in .env or backend/.env", file=sys.stderr)
    sys.exit(1)

print(f"--- Groq Spike Test ---")
print(f"Model: {model_name}")
print(f"API Key: {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '***'}")

try:
    from groq import Groq
except ImportError as e:
    print(f"ERROR: groq package is not installed: {e}", file=sys.stderr)
    sys.exit(1)

client = Groq(api_key=api_key, timeout=30.0)

# Step 1: Basic text call
print("\n[Step 1] Running standard chat completion...")
try:
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a concise negotiation assistant."},
            {"role": "user", "content": "Provide a 1-sentence tip on challenging SaaS support fees."}
        ],
        temperature=0.2,
        max_tokens=100
    )
    content = response.choices[0].message.content
    print(f"Response: {content}")
except Exception as e:
    print(f"ERROR in standard chat completion: {e}", file=sys.stderr)
    sys.exit(1)

# Step 2: JSON mode call validated by Pydantic
class TestNegotiationAdvice(BaseModel):
    vendor: str
    tactic: str
    rationale: str
    estimated_saving_pct: float

print("\n[Step 2] Running JSON-mode chat completion with Pydantic validation...")
try:
    json_response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a SaaS procurement agent. Respond ONLY with a valid JSON object matching this schema: "
                    '{"vendor": str, "tactic": str, "rationale": str, "estimated_saving_pct": float}'
                )
            },
            {
                "role": "user",
                "content": "Generate advice for negotiating with MeghMonitor cloud monitoring."
            }
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    raw_json = json_response.choices[0].message.content
    print(f"Raw JSON output:\n{raw_json}")
    
    parsed = json.loads(raw_json)
    validated = TestNegotiationAdvice.model_validate(parsed)
    print("\nPydantic validation PASSED:")
    print(f"  Vendor:    {validated.vendor}")
    print(f"  Tactic:    {validated.tactic}")
    print(f"  Rationale: {validated.rationale}")
    print(f"  Estimated: {validated.estimated_saving_pct}%")
except Exception as e:
    print(f"ERROR in JSON-mode completion: {e}", file=sys.stderr)
    sys.exit(1)

print("\n--- GROQ SPIKE RESULT: PASS ---")
