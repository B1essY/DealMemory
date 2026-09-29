import type {
  Negotiation,
  Outcome,
  BriefingResult,
  SeedStatus,
  SystemHealth,
  EvalResults
} from '../types';

const API_BASE = 'http://localhost:8000';

export async function fetchHealthDetailed(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/health/detailed`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSeedStatus(): Promise<SeedStatus> {
  const res = await fetch(`${API_BASE}/api/demo/status`);
  if (!res.ok) throw new Error(`Failed to fetch seed status: ${res.statusText}`);
  return res.json();
}

export async function seedDemoData(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/demo/seed`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Seeding failed');
  }
  return res.json();
}

export async function resetDemoData(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/demo/reset`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Reset failed');
  return res.json();
}

export async function fetchNegotiations(): Promise<Negotiation[]> {
  const res = await fetch(`${API_BASE}/api/negotiations`);
  if (!res.ok) throw new Error('Failed to fetch negotiations');
  return res.json();
}

export async function fetchNegotiation(id: string): Promise<Negotiation> {
  const res = await fetch(`${API_BASE}/api/negotiations/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch deal ${id}`);
  return res.json();
}

export async function createNegotiation(data: Partial<Negotiation>): Promise<Negotiation> {
  const res = await fetch(`${API_BASE}/api/negotiations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Failed to create deal');
  }
  return res.json();
}

export async function analyzeDeal(id: string, useMemory: boolean): Promise<BriefingResult> {
  const res = await fetch(`${API_BASE}/api/negotiations/${id}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ use_memory: useMemory })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Analysis briefing failed');
  }
  return res.json();
}

export async function recordOutcome(id: string, data: any): Promise<Outcome> {
  const res = await fetch(`${API_BASE}/api/negotiations/${id}/outcome`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Outcome retention failed');
  }
  return res.json();
}

export async function testRecall(query: string, budget = 'high'): Promise<any> {
  const res = await fetch(`${API_BASE}/api/memory/recall`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, budget, max_tokens: 2048 })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Recall test failed');
  }
  return res.json();
}

export async function fetchMemoryStats(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/memory/stats`);
  if (!res.ok) throw new Error('Failed to fetch memory stats');
  return res.json();
}

export async function fetchLearnedPatterns(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/learning/patterns`);
  if (!res.ok) throw new Error('Failed to fetch learned patterns');
  return res.json();
}

export async function fetchEvalResults(): Promise<EvalResults | any> {
  const res = await fetch(`${API_BASE}/api/eval/results`);
  if (!res.ok) throw new Error('Failed to fetch evaluation results');
  return res.json();
}

export async function triggerEvalRun(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/eval/run`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Evaluation run failed');
  }
  return res.json();
}
