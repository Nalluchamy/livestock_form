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
  grading_event_id?: string;
}

export type ReviewStatus = 'PENDING' | 'IN_REVIEW' | 'RESOLVED' | 'ESCALATED' | 'CANCELLED';

export interface ReviewItem {
  id: string;
  grading_event_id: string | null;
  original_human_grade: GradeLevel;
  original_system_grade: GradeLevel;
  expert_grade: GradeLevel | null;
  status: ReviewStatus;
  reviewer_id: string | null;
  reviewer_action: string | null;
  reviewer_final_decision: GradeLevel | null;
  reviewer_rationale: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}

export interface ReviewStats {
  total_reviews: number;
  pending_count: number;
  in_review_count: number;
  resolved_count: number;
  escalated_count: number;
  cancelled_count: number;
  upheld_human_count: number;
  accepted_system_count: number;
  expert_override_count: number;
}

export interface ReviewsResponseData {
  total: number;
  reviews: ReviewItem[];
  stats: ReviewStats;
}

export interface ResolveReviewPayload {
  reviewer_id: string;
  reviewer_action: 'UPHELD_HUMAN' | 'ACCEPTED_SYSTEM' | 'EXPERT_OVERRIDE' | 'ESCALATE_TO_SENIOR' | 'DISMISSED';
  reviewer_final_decision: GradeLevel;
  reviewer_rationale: string;
}

export interface ExperimentData {
  id: string;
  experiment_name: string;
  dataset_version: string;
  model_version: string;
  evaluation_timestamp: string;
  evaluation_type: 'synthetic' | 'retrospective_real' | 'prospective_human_assisted';
  status: string;
  dataset_sample_count: number;
  test_sample_count: number;
  performance_metrics: Record<string, any>;
  expert_agreement_metrics: Record<string, any>;
  confidence_distribution: Record<string, any>;
  error_category_counts: Record<string, any>;
  notes?: string;
  created_at: string;
}

export interface DatasetInfoData {
  real_dataset: {
    status: string;
    raw_images_count: number;
    processed_images_count: number;
    total_annotations: number;
    complete_consensus_annotations: number;
    pending_annotations: number;
    disagreements_count: number;
    inter_expert_kappa: number | null;
    inter_expert_exact_pct: number | null;
    manifest: Record<string, any>;
    privacy_compliance: {
      exif_stripping_enforced: boolean;
      pii_manual_review_active: boolean;
      prohibit_ai_expert_labels: boolean;
    };
  };
  synthetic_dataset: {
    status: string;
    sample_count: number;
    description: string;
    storage: string;
  };
  active_evaluation_mode: string;
  ready_for_real_evaluation: boolean;
  message: string;
}

export interface MetricsData {
  total_gradings: number;
  agreement_rate: number;
  disagreement_rate: number;
  average_confidence: number;
  pending_reviews: number;
  resolved_reviews?: number;
  low_confidence_cases: number;
  grade_distribution?: Record<string, number>;
  latest_experiment?: ExperimentData | null;
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
