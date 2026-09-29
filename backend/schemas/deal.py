"""
DealMemory Pydantic Schemas
Defines request and response schemas for Negotiations, Briefings, Outcomes, and Memory.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ----------------- NEGOTIATION SCHEMAS -----------------

class TacticAttempt(BaseModel):
    tactic: str
    vendor_response: str
    success: bool

class NegotiationCreate(BaseModel):
    vendor: str = Field(..., description="Vendor name, e.g. KavachSec")
    product: str = Field(..., description="Product name, e.g. Kavach Endpoint Shield")
    category: str = Field(..., description="Software category, e.g. Cybersecurity")
    seats: int = Field(..., gt=0, description="Number of user licences or nodes")
    initial_quote: float = Field(..., gt=0, description="Initial quote in INR")
    contract_duration_months: int = Field(default=12, gt=0, description="Duration in months")
    support_fee: float = Field(default=0.0, ge=0, description="Quoted support fee in INR")
    renewal_type: str = Field(default="New", description="New or Renewal")
    deadline: str = Field(..., description="Expected decision date YYYY-MM-DD")
    clauses_raised: List[str] = Field(default_factory=list, description="Specific terms or clauses under negotiation")
    notes: Optional[str] = Field(default="", description="Procurement notes or background")

class NegotiationResponse(NegotiationCreate):
    id: str
    is_analyzed: bool = False
    is_seeded: bool = False
    created_at: str

# ----------------- OUTCOME SCHEMAS -----------------

class OutcomeCreate(BaseModel):
    final_price: float = Field(..., gt=0, description="Final negotiated price in INR")
    contract_duration_months: Optional[int] = Field(default=12, description="Agreed duration in months")
    tactics_attempted: List[TacticAttempt] = Field(default_factory=list, description="Tactics used and vendor response")
    vendor_response: str = Field(..., description="Summary of overall vendor negotiation stance")
    successful_tactics: List[str] = Field(default_factory=list, description="Tactics that worked")
    failed_tactics: List[str] = Field(default_factory=list, description="Tactics that failed or produced zero concession")
    terms_accepted_rejected: str = Field(..., description="What terms company accepted vs refused")
    lessons_learned: str = Field(..., description="Key takeaway for future negotiations")
    notes: Optional[str] = Field(default="", description="Additional debrief notes")

class OutcomeResponse(OutcomeCreate):
    id: str
    negotiation_id: str
    retained_to_hindsight: bool
    hindsight_doc_id: Optional[str] = None
    created_at: str

# ----------------- EVIDENCE & BRIEFING SCHEMAS -----------------

class HistoricalEvidenceItem(BaseModel):
    claim: str = Field(..., description="Specific factual claim derived from recalled memory")
    supporting_memory_id: str = Field(..., description="Exact Hindsight memory ID or internal mapped reference (no invented IDs)")
    source_excerpt_or_reference: str = Field(..., description="Exact quote or reference from recalled memory")
    relevance: str = Field(..., description="Why this evidence applies to the current deal")

class LearnedPatternItem(BaseModel):
    tactic: str = Field(..., description="Name of the negotiation tactic")
    successes: int = Field(..., ge=0, description="Number of observed successes in recalled memories")
    attempts: int = Field(..., ge=0, description="Total attempts observed in recalled memories")
    success_rate: float = Field(..., ge=0.0, le=100.0, description="Success rate percentage (successes / attempts * 100)")
    supporting_memory_citations: List[str] = Field(default_factory=list, description="IDs of memories evidencing this pattern")
    interpretation: str = Field(..., description="Strategic interpretation of this pattern for procurement")

class RecommendedTactic(BaseModel):
    rank: int = Field(..., ge=1, le=5, description="Rank from 1 to 5")
    tactic: str = Field(..., description="Specific tactic to execute")
    reason: str = Field(..., description="Strategic reasoning for recommendation")
    supporting_evidence: str = Field(..., description="Direct citation to recalled evidence (or best-practice if OFF)")
    confidence: str = Field(..., description="High, Medium, or Low")

class BriefingSchema(BaseModel):
    use_memory: bool = Field(..., description="Whether Hindsight memory was active")
    target_price: float = Field(default=0.0, description="Target counter-offer in INR")
    walk_away_price: float = Field(default=0.0, description="Maximum ceiling price before walking away in INR")
    target_price_reasoning: str = Field(default="Derived from target discount benchmarks and quote parameters.", description="Quantitative and tactical basis for target price")
    walk_away_price_reasoning: str = Field(default="Threshold based on budget and initial quote ceiling.", description="Basis for ceiling price threshold")
    confidence: str = Field(default="Medium", description="Overall confidence: High, Medium, or Low")
    historical_evidence: List[HistoricalEvidenceItem] = Field(
        default_factory=list,
        description="Historical claims grounded strictly in Hindsight recall"
    )
    learned_patterns: List[LearnedPatternItem] = Field(
        default_factory=list,
        description="Cross-deal or vendor patterns derived from recalled memories"
    )
    recommended_tactics: List[RecommendedTactic] = Field(
        default_factory=list,
        description="Ranked 1-3 recommended negotiation tactics"
    )
    tactics_to_avoid: List[str] = Field(
        default_factory=list,
        description="Tactics known to fail or backfire"
    )
    temporal_observations: List[str] = Field(
        default_factory=list,
        description="Timing or fiscal quarter observations supported by data"
    )
    uncertainty_caveats: List[str] = Field(
        default_factory=list,
        description="Gaps, weak evidence, or conflicting data observations"
    )

# ----------------- API REQUEST / RESPONSE SCHEMAS -----------------

class AnalyzeRequest(BaseModel):
    use_memory: bool = Field(default=True, description="True for ON (with Hindsight), False for OFF baseline")

class RecallQueryRequest(BaseModel):
    query: str
    types: Optional[List[str]] = None
    budget: Optional[str] = "high"
    max_tokens: Optional[int] = 2048

class SeedStatusResponse(BaseModel):
    is_seeded: bool
    seeded_count: int
    skipped_count: int
    verified_count: int
    hindsight_connected: bool
    details: Optional[str] = None
