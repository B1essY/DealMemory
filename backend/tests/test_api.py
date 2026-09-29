"""
DealMemory Backend Test Suite
Tests health, negotiations, schema validation, and error states.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "DealMemory" in data["service"]

def test_health_detailed_endpoint(client):
    response = client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert "sqlite" in data["services"]
    assert "hindsight" in data["services"]
    assert "groq" in data["services"]

def test_create_and_get_negotiation(client):
    payload = {
        "vendor": "VyaparPulse",
        "product": "Pulse CRM Growth",
        "category": "CRM",
        "seats": 50,
        "initial_quote": 1200000.0,
        "contract_duration_months": 12,
        "support_fee": 150000.0,
        "renewal_type": "New",
        "deadline": "2026-12-01",
        "clauses_raised": ["Multi-year price lock", "Quarterly payment schedule"],
        "notes": "Testing unit test negotiation persistence."
    }
    
    # 1. Create deal
    res = client.post("/api/negotiations", json=payload)
    assert res.status_code == 200
    data = res.json()
    deal_id = data["id"]
    assert data["vendor"] == "VyaparPulse"
    assert data["initial_quote"] == 1200000.0

    # 2. Get deal
    get_res = client.get(f"/api/negotiations/{deal_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["id"] == deal_id
    assert get_data["product"] == "Pulse CRM Growth"

def test_invalid_negotiation_payload(client):
    bad_payload = {
        "vendor": "TestVendor",
        # Missing required product, category, initial_quote
        "seats": -5  # Invalid seats
    }
    res = client.post("/api/negotiations", json=bad_payload)
    assert res.status_code == 422  # Unprocessable Entity

def test_negotiation_not_found(client):
    res = client.get("/api/negotiations/non_existent_deal_xyz")
    assert res.status_code == 404

def test_demo_status_endpoint(client):
    res = client.get("/api/demo/status")
    assert res.status_code == 200
    data = res.json()
    assert "is_seeded" in data
    assert "seeded_count" in data
    assert "hindsight_connected" in data

def test_eval_results_endpoint(client):
    res = client.get("/api/eval/results")
    assert res.status_code == 200
