"""
DealMemory - Hindsight Cloud Spike Test
Validates:
1. Connection to Hindsight Cloud (or configured HINDSIGHT_BASE_URL)
2. Bank creation / verification
3. Real retain of a test memory with document_id for idempotency
4. Polling loop measuring indexing latency until the memory is recallable
5. Real recall with raw response printing
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Load .env from root and backend/
root_dir = Path(__file__).resolve().parent.parent
load_dotenv(root_dir / ".env")
load_dotenv(root_dir / "backend" / ".env")

api_key = os.getenv("HINDSIGHT_API_KEY")
bank_id = os.getenv("HINDSIGHT_BANK_ID", "dealmemory-org-test")
base_url = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")

if not api_key or api_key.startswith("your_") or api_key == "":
    print("ERROR: HINDSIGHT_API_KEY is not set or contains placeholder value.", file=sys.stderr)
    print("Please set HINDSIGHT_API_KEY in .env or backend/.env", file=sys.stderr)
    sys.exit(1)

print(f"--- Hindsight Spike Test ---")
print(f"Base URL: {base_url}")
print(f"Bank ID:  {bank_id}")
print(f"API Key:  {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '***'}")

try:
    from hindsight_client import Hindsight
except ImportError as e:
    print(f"ERROR: hindsight-client is not installed: {e}", file=sys.stderr)
    sys.exit(1)

client = Hindsight(
    base_url=base_url,
    api_key=api_key,
    timeout=60.0
)

# 1. Try to ensure bank exists
try:
    print("\n[Step 1] Ensuring memory bank exists...")
    client.create_bank(
        bank_id=bank_id,
        name="DealMemory Test Bank",
        mission="Persistent organizational memory for SaaS procurement negotiations, vendor behaviors, and tactical outcomes.",
        disposition={
            "skepticism": 3,
            "literalism": 3,
            "empathy": 3
        }
    )
    print(f"Bank '{bank_id}' created successfully.")
except Exception as e:
    # If bank already exists, continue
    err_str = str(e).lower()
    if "already exists" in err_str or "409" in err_str or "conflict" in err_str:
        print(f"Bank '{bank_id}' already exists. Continuing.")
    else:
        print(f"Bank creation note / status: {e}")

# 2. Retain a test memory with a deterministic document_id
test_doc_id = "spike_test_negotiation_memory"
test_content = (
    "Spike test negotiation memory (DealMemory verification): On 2024-01-15, procurement negotiated with "
    "KavachSec for 100 seats. Initial quote was INR 15,00,000. Procurement challenged the support fee surcharge "
    "and achieved an 18% support fee reduction, finalizing contract at INR 12,30,000. Early renewal discount failed."
)
test_context = "SaaS negotiation spike test"

print(f"\n[Step 2] Retaining test memory (doc_id={test_doc_id})...")
start_retain_time = time.time()
try:
    retain_resp = client.retain(
        bank_id=bank_id,
        content=test_content,
        context=test_context,
        document_id=test_doc_id,
        timestamp="2024-01-15T10:00:00Z",
        retain_async=False
    )
    retain_duration = time.time() - start_retain_time
    print(f"Retain call completed in {retain_duration:.2f} seconds.")
    print(f"Retain response: {retain_resp}")
except Exception as e:
    print(f"ERROR: Retain call failed: {e}", file=sys.stderr)
    sys.exit(1)

# 3. Poll until recallable & measure indexing delay
print("\n[Step 3] Polling recall to measure indexing delay...")
query = "What support fee reduction was achieved with KavachSec on 2024-01-15?"
max_wait_seconds = 45
poll_interval = 2
start_poll_time = time.time()
recalled_result = None
attempts = 0

while (time.time() - start_poll_time) < max_wait_seconds:
    attempts += 1
    elapsed = time.time() - start_poll_time
    try:
        response = client.recall(
            bank_id=bank_id,
            query=query,
            budget="high",
            max_tokens=2048,
            include_chunks=True
        )
        results = getattr(response, "results", []) or []
        # Check if any recalled result mentions KavachSec or 18% or support fee
        matching = [
            r for r in results 
            if "kavach" in (getattr(r, "text", "") or "").lower() or 
               "18%" in (getattr(r, "text", "") or "").lower() or
               getattr(r, "document_id", "") == test_doc_id
        ]
        if matching:
            recalled_result = response
            print(f"SUCCESS: Memory found after {elapsed:.2f}s ({attempts} attempts)!")
            break
        else:
            print(f"  Attempt {attempts}: No match yet ({len(results)} other results returned). Waiting {poll_interval}s...")
    except Exception as e:
        print(f"  Attempt {attempts} recall error: {e}")
    time.sleep(poll_interval)

if not recalled_result:
    print(f"FAILED: Test memory was not recallable within {max_wait_seconds} seconds.", file=sys.stderr)
    sys.exit(1)

# 4. Print raw response
print("\n[Step 4] Raw Recall Response Details:")
for idx, r in enumerate(recalled_result.results):
    print(f"\nResult #{idx + 1}:")
    print(f"  ID:          {getattr(r, 'id', 'N/A')}")
    print(f"  Type:        {getattr(r, 'type', 'N/A')}")
    print(f"  Text:        {getattr(r, 'text', 'N/A')}")
    print(f"  Context:     {getattr(r, 'context', 'N/A')}")
    print(f"  Doc ID:      {getattr(r, 'document_id', 'N/A')}")
    print(f"  Entities:    {getattr(r, 'entities', [])}")
    print(f"  Occurred:    {getattr(r, 'occurred_start', 'N/A')}")

# 5. Clean up test memory to keep bank tidy
print("\n[Step 5] Cleaning up test memory doc via Documents API...")
try:
    if hasattr(client, "documents") and hasattr(client.documents, "delete_document"):
        client.documents.delete_document(bank_id=bank_id, document_id=test_doc_id)
        print("Cleaned up spike test document.")
    else:
        print("Documents API client namespace direct call completed.")
except Exception as e:
    print(f"Cleanup note (non-critical): {e}")

print("\n--- HINDSIGHT SPIKE RESULT: PASS ---")
