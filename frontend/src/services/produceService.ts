import { apiClient } from './api';

export interface ProduceGradePayload {
  surface_defect_pct?: number;
  ripeness_stage?: string;
  color_uniformity_pct?: number;
  bruising_severity?: string;
  shape_circularity?: number;
  aspect_ratio?: number;
  critical_defects?: string[];
  laplacian_var?: number;
  illumination_mean?: number;
  surface_occlusion_pct?: number;
  human_grade?: string;
  create_persistent_review?: boolean;
}

export interface ProduceDatasetStatus {
  status: string;
  processed_samples_count: number;
  raw_samples_count: number;
  target_range: string;
  transparency_note: string;
}

export interface ProduceExperimentSummary {
  status: string;
  message?: string;
  experiment_id?: string;
  experiment_name?: string;
  dataset_version?: string;
  timestamp?: string;
  targets: Record<string, number>;
  measured_results?: Record<string, any>;
  sample_count_baseline?: number;
  sample_count_assisted?: number;
  is_synthetic: boolean;
}

export interface ProduceEdgeCase {
  case_id: string;
  title: string;
  input_conditions: Record<string, any>;
  expected_behavior: string;
  observed_behavior: string;
  failure_etiology: string;
  corrective_action: string;
}

export const getProduceDatasetStatus = async (): Promise<ProduceDatasetStatus> => {
  const resp = await apiClient.get('/produce/dataset-status');
  return resp.data.data;
};

export const getProduceExperimentSummary = async (): Promise<ProduceExperimentSummary> => {
  const resp = await apiClient.get('/produce/experiments/summary');
  return resp.data.data;
};

export const getProduceEdgeCases = async (): Promise<ProduceEdgeCase[]> => {
  const resp = await apiClient.get('/produce/edge-cases');
  return resp.data.data.edge_cases;
};

export const gradeProduceSample = async (payload: ProduceGradePayload): Promise<any> => {
  const resp = await apiClient.post('/produce/grade', payload);
  return resp.data.data;
};

export const uploadAndGradeProduce = async (formData: FormData): Promise<any> => {
  const resp = await apiClient.post('/produce/upload-and-grade', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return resp.data.data;
};

export interface RealProduceStatus {
  status: string;
  dataset_type: string;
  is_synthetic: boolean;
  is_real: boolean;
  real_images_collected: number;
  real_images_required: number;
  real_images_remaining: number;
  recommended_target: number;
  collection_categories?: {
    apparent_high_quality: number;
    apparent_minor_defects: number;
    apparent_substantial_defects: number;
  };
  expert_annotation_status?: string;
  images_annotated: number;
  consensus_samples: number;
  disagreements: number;
  adjudicated_samples: number;
  isolation_statement: string;
  data_integrity_rule: string;
}

export interface RealProduceSample {
  sample_id: string;
  filename: string;
  source_type: string;
  capture_date: string;
  capture_environment: string;
  camera_type: string;
  collection_category: string;
  annotation_status: string;
  review_status: string;
  image_quality_status: string;
  defect_pct: number;
  ripeness_stage: string;
  occlusion_pct: number;
  grader_1_grade: string | null;
  grader_2_grade: string | null;
  ground_truth_grade: string | null;
  adjudicated_grade: string | null;
  is_blind_masked: boolean;
}

export interface StakeholderStatus {
  status: string;
  total_participants: number;
  message: string;
  tasks: Array<{ id: string; name: string; description: string }>;
  survey_questions: Array<{ id: string; text: string }>;
  mean_scores: Record<string, number>;
  task_completion_rates: Record<string, number>;
  qualitative_feedback: Array<{
    participant_id: string;
    role: string;
    missing_info: string;
    override_scenarios: string;
    speed_improvements: string;
  }>;
  ethical_safeguards: string;
}

export interface ProduceFailureCase {
  case_id: string;
  title: string;
  category: string;
  input_conditions: Record<string, any>;
  detected_features: Record<string, any>;
  predicted_grade: string;
  human_grade: string;
  failure_mechanism: string;
  corrective_action: string;
  retake_recommended: boolean;
}

export const getRealProduceStatus = async (): Promise<RealProduceStatus> => {
  const resp = await apiClient.get('/produce/real/status');
  return resp.data.data;
};

export const listRealProduceSamples = async (params?: {
  status?: string;
  viewer_id?: string;
  is_senior?: boolean;
}): Promise<{ samples: RealProduceSample[]; total: number }> => {
  const resp = await apiClient.get('/produce/real/samples', { params });
  return resp.data.data;
};

export const uploadRealProduceImage = async (formData: FormData): Promise<any> => {
  const resp = await apiClient.post('/produce/real/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return resp.data.data;
};

export const batchUploadRealProduce = async (formData: FormData): Promise<any> => {
  const resp = await apiClient.post('/produce/real/batch-upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return resp.data.data;
};

export const submitRealProduceGrade = async (payload: {
  sample_id: string;
  grader_id?: string;
  grade: string;
  confidence?: number;
  notes?: string;
}): Promise<any> => {
  const resp = await apiClient.post('/produce/real/annotate', payload);
  return resp.data.data;
};

export const adjudicateRealProduce = async (payload: {
  sample_id: string;
  reviewer_id?: string;
  final_grade: string;
  rationale: string;
}): Promise<any> => {
  const resp = await apiClient.post('/produce/real/adjudicate', payload);
  return resp.data.data;
};

export const generateRealProduceSplits = async (): Promise<any> => {
  const resp = await apiClient.post('/produce/real/splits');
  return resp.data.data;
};

export const runRealProduceExperiment = async (payload?: { experiment_name?: string }): Promise<any> => {
  const resp = await apiClient.post('/produce/real/experiment', payload || {});
  return resp.data.data;
};

export const getStakeholderStatus = async (): Promise<StakeholderStatus> => {
  const resp = await apiClient.get('/produce/stakeholder/status');
  return resp.data.data;
};

export const submitStakeholderFeedback = async (payload: {
  participant_id?: string;
  role: string;
  completed_tasks: Record<string, boolean>;
  likert_scores: Record<string, number>;
  qualitative_feedback: Record<string, string>;
}): Promise<any> => {
  const resp = await apiClient.post('/produce/stakeholder/submit', payload);
  return resp.data.data;
};

export const getProduceFailureCases = async (): Promise<ProduceFailureCase[]> => {
  const resp = await apiClient.get('/produce/real/failure-cases');
  return resp.data.data.failure_cases;
};

export interface SyntheticDatasetStatus {
  status: string;
  dataset_name?: string;
  version?: string;
  detected_backend?: string;
  verified_images_count: number;
  target_total_samples: number;
  missing_quota_samples_count: number;
  qc_summary?: {
    qc_pass_count: number;
    qc_review_flagged_count: number;
    qc_fail_count: number;
    duplicates_detected: number;
  };
  isolation_guarantee: string;
}

export interface SyntheticBenchmarkResults {
  benchmark_name: string;
  timestamp: string;
  evaluation_type: string;
  is_synthetic: boolean;
  dataset_version: string;
  total_images_evaluated: number;
  optical_quality_gate: {
    passed_count: number;
    rejected_count: number;
    rejection_rate_pct: number;
  };
  metrics: {
    commercial_samples_count: number;
    commercial_correct_count: number;
    accuracy_pct: number;
    per_class: Record<string, {
      true_positives: number;
      false_positives: number;
      false_negatives: number;
      precision_pct: number;
      recall_pct: number;
      f1_score: number;
    }>;
  };
  confusion_matrix: Record<string, Record<string, number>>;
  sample_evaluations: Array<{
    sample_id: string;
    filename: string;
    category: string;
    expected_grade: string;
    derived_grade: string;
    confidence: number;
    quality_passed: boolean;
    review_required: boolean;
    triggered_rules: string[];
  }>;
  non_fabrication_declaration: string;
}

export const getSyntheticDatasetStatus = async (): Promise<SyntheticDatasetStatus> => {
  const resp = await apiClient.get('/produce/synthetic-status');
  return resp.data.data;
};

export const getSyntheticBenchmarkResults = async (): Promise<SyntheticBenchmarkResults> => {
  const resp = await apiClient.get('/produce/synthetic-benchmark-results');
  return resp.data.data;
};

export const runSyntheticBenchmark = async (payload?: { experiment_name?: string }): Promise<any> => {
  const resp = await apiClient.post('/produce/synthetic-benchmark', payload || {});
  return resp.data.data;
};


