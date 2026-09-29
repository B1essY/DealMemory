export interface TacticAttempt {
  tactic: string;
  vendor_response: string;
  success: boolean;
}

export interface Negotiation {
  id: string;
  vendor: string;
  product: string;
  category: string;
  seats: number;
  initial_quote: number;
  contract_duration_months: number;
  support_fee: number;
  renewal_type: string;
  deadline: string;
  clauses_raised: string[];
  notes?: string;
  is_analyzed: boolean;
  is_seeded: boolean;
  created_at: string;
}

export interface Outcome {
  id: string;
  negotiation_id: string;
  final_price: number;
  contract_duration_months?: number;
  tactics_attempted: TacticAttempt[];
  vendor_response: string;
  successful_tactics: string[];
  failed_tactics: string[];
  terms_accepted_rejected: string;
  lessons_learned: string;
  notes?: string;
  retained_to_hindsight: boolean;
  hindsight_doc_id?: string;
  created_at: string;
}

export interface HistoricalEvidenceItem {
  claim: string;
  supporting_memory_id: string;
  source_excerpt_or_reference: string;
  relevance: string;
}

export interface LearnedPatternItem {
  tactic: string;
  successes: number;
  attempts: number;
  success_rate: number;
  supporting_memory_citations: string[];
  interpretation: string;
}

export interface RecommendedTactic {
  rank: number;
  tactic: string;
  reason: string;
  supporting_evidence: string;
  confidence: 'High' | 'Medium' | 'Low' | string;
}

export interface Briefing {
  use_memory: boolean;
  historical_evidence: HistoricalEvidenceItem[];
  learned_patterns: LearnedPatternItem[];
  recommended_tactics: RecommendedTactic[];
  tactics_to_avoid: string[];
  target_price: number;
  walk_away_price: number;
  target_price_reasoning: string;
  walk_away_price_reasoning: string;
  temporal_observations: string[];
  uncertainty_caveats: string[];
  confidence: 'High' | 'Medium' | 'Low' | string;
}

export interface RecallStats {
  vendor_query: string;
  vendor_memories_count: number;
  pattern_query: string;
  pattern_memories_count: number;
  total_unique_memories: number;
}

export interface BriefingResult {
  briefing_id: string;
  deal_id: string;
  briefing: Briefing;
  recall_stats: RecallStats;
  recalled_memories: Array<{
    id: string;
    text: string;
    type: string;
    context: string;
    document_id: string;
    entities: string[];
    occurred_start?: string;
  }>;
}

export interface SeedStatus {
  is_seeded: boolean;
  seeded_count: number;
  skipped_count: number;
  verified_count: number;
  hindsight_connected: boolean;
  details?: string;
}

export interface SystemHealth {
  status: 'ready' | 'degraded';
  services: {
    sqlite: { status: string; message: string };
    hindsight: { status: string; message: string };
    groq: { status: string; message: string };
  };
}

export interface EvalLearningCurvePoint {
  deal_id: string;
  experience_count: number;
  off_target_price_error: number;
  on_target_price_error: number;
  error_reduction_pct: number;
}

export interface EvalResults {
  evaluation_label: string;
  disclaimer: string;
  evaluated_deals_count: number;
  overall_metrics: {
    mean_target_price_error: {
      off_mode: number;
      on_mode: number;
      improvement_factor: string;
    };
    winning_tactic_top3_hit_rate: {
      off_mode: string;
      on_mode: string;
    };
    avoided_mistake_rate: {
      off_mode: string;
      on_mode: string;
    };
  };
  learning_curve: EvalLearningCurvePoint[];
  deal_evaluations: any[];
  timestamp: string;
}
