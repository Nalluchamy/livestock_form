export type GradeLevel = 'A' | 'B' | 'C' | 'D';

export interface AttributeInput {
  body_condition: number;
  coat_quality: string;
  eye_condition: string;
  wound_presence: string;
  mobility: string;
  appetite: string;
}

export interface GradeRequestPayload {
  sample_id?: string;
  grader_id?: string;
  image_id?: string;
  human_grade?: GradeLevel;
  attributes: Record<string, any>;
}

export interface GradeResultData {
  grading_event_id: string;
  grade: GradeLevel;
  confidence: number;
  reasons: string[];
  missing_attributes: string[];
  review_required: boolean;
  sample_id: string;
  grader_id: string;
  generated_demo_entities: boolean;
}

export interface APIResponse<T> {
  status: 'success' | 'error';
  message: string;
  data: T;
}

export interface GradingEventHistoryItem {
  id: string;
  human_grade: GradeLevel | null;
  ai_grade: GradeLevel;
  confidence_score: number;
  review_status: 'pending' | 'completed';
  created_at: string;
}

export interface SingleGradingEventDetail extends GradingEventHistoryItem {
  explanation: string[];
}

export interface GradingEventHistoryResponse {
  total: number;
  events: GradingEventHistoryItem[];
}

export interface DisagreementRequestPayload {
  human_grade: GradeLevel;
  system_grade: GradeLevel;
  reason: string;
}

export interface MetricsData {
  total_gradings: number;
  agreement_rate: number;
  disagreement_rate: number;
  average_confidence: number;
  pending_reviews: number;
  low_confidence_cases: number;
}

export interface AgreementMetricSet {
  cohen_kappa: number;
  exact_match_pct: number;
  adjacent_match_pct: number;
}

export interface AgreementMetricsData {
  dataset_info: {
    total_samples: number;
    source: string;
    provenance: string;
  };
  human_baseline: AgreementMetricSet;
  rule_engine_vs_consensus: AgreementMetricSet;
  decision_tree_ml_vs_consensus: AgreementMetricSet;
  decision_tree_ml_vs_grader_1: AgreementMetricSet;
  decision_tree_ml_vs_grader_2: AgreementMetricSet;
}

