import { apiClient } from './api';

export interface AnnotationItem {
  id: string;
  sample_id: string;
  image_path: string;
  species: string;
  body_condition?: number | null;
  coat_quality?: string | null;
  eye_condition?: string | null;
  wound_presence?: string | null;
  mobility?: string | null;
  appetite?: string | null;
  weight_if_available?: number | null;
  expert_grader_1_id?: string | null;
  expert_grade_1?: string | null;
  expert_grade_1_notes?: string | null;
  expert_grade_1_submitted_at?: string | null;
  expert_grader_2_id?: string | null;
  expert_grade_2?: string | null;
  expert_grade_2_notes?: string | null;
  expert_grade_2_submitted_at?: string | null;
  final_consensus_grade?: string | null;
  consensus_reviewer_id?: string | null;
  consensus_rationale?: string | null;
  consensus_reached_at?: string | null;
  annotation_status: 'PENDING' | 'PARTIALLY_ANNOTATED' | 'CONSENSUS_REACHED' | 'DISAGREEMENT' | 'REJECTED';
  quality_flagged: boolean;
  quality_issue_reason?: string | null;
  flagged_by_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AnnotationStats {
  total_samples: number;
  pending_samples: number;
  partially_annotated_samples: number;
  consensus_reached_samples: number;
  disagreement_samples: number;
  rejected_samples: number;
  quality_flagged_samples: number;
  double_graded_samples: number;
  exact_agreement_percentage: number;
}

export const getAnnotations = async (params?: {
  status?: string;
  quality_flagged?: boolean;
  viewer_id?: string;
  is_senior?: boolean;
  skip?: number;
  limit?: number;
}): Promise<{ total: number; skip: number; limit: number; items: AnnotationItem[] }> => {
  const response = await apiClient.get('/annotations', { params });
  return response.data.data;
};

export const getAnnotationBySampleId = async (
  sampleId: string,
  viewerId?: string,
  isSenior?: boolean
): Promise<AnnotationItem> => {
  const response = await apiClient.get(`/annotations/${sampleId}`, {
    params: { viewer_id: viewerId, is_senior: isSenior },
  });
  return response.data.data;
};

export const submitGrade = async (
  sampleId: string,
  payload: {
    grader_id: string;
    grade: string;
    attributes?: Record<string, any>;
    notes?: string;
  }
): Promise<AnnotationItem> => {
  const response = await apiClient.post(`/annotations/${sampleId}/grade`, payload);
  return response.data.data;
};

export const adjudicateConsensus = async (
  sampleId: string,
  payload: {
    reviewer_id: string;
    final_grade: string;
    rationale: string;
  }
): Promise<AnnotationItem> => {
  const response = await apiClient.post(`/annotations/${sampleId}/consensus`, payload);
  return response.data.data;
};

export const flagQuality = async (
  sampleId: string,
  payload: {
    grader_id: string;
    reason: string;
  }
): Promise<AnnotationItem> => {
  const response = await apiClient.post(`/annotations/${sampleId}/flag-quality`, payload);
  return response.data.data;
};

export const getAnnotationStats = async (): Promise<AnnotationStats> => {
  const response = await apiClient.get('/annotations/stats/summary');
  return response.data.data;
};

export const uploadDatasetImage = async (formData: FormData): Promise<any> => {
  const response = await apiClient.post('/dataset/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data.data;
};
