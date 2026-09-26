import { apiClient } from './api';
import { 
  APIResponse, 
  ReviewsResponseData, 
  ReviewItem, 
  DisagreementRequestPayload, 
  ResolveReviewPayload 
} from '../types';

export const getReviews = async (status?: string, skip = 0, limit = 50): Promise<ReviewsResponseData> => {
  const params: Record<string, any> = { skip, limit };
  if (status && status !== 'ALL') {
    params.status = status;
  }
  const response = await apiClient.get<APIResponse<ReviewsResponseData>>('/reviews', { params });
  return response.data.data;
};

export const getReviewById = async (id: string): Promise<ReviewItem> => {
  const response = await apiClient.get<APIResponse<ReviewItem>>(`/reviews/${id}`);
  return response.data.data;
};

export const createReview = async (payload: DisagreementRequestPayload): Promise<ReviewItem> => {
  const response = await apiClient.post<APIResponse<ReviewItem>>('/reviews', {
    grading_event_id: payload.grading_event_id,
    original_human_grade: payload.human_grade,
    original_system_grade: payload.system_grade,
    reviewer_rationale: payload.reason,
  });
  return response.data.data;
};

export const resolveReview = async (id: string, payload: ResolveReviewPayload): Promise<ReviewItem> => {
  const response = await apiClient.post<APIResponse<ReviewItem>>(`/reviews/${id}/resolve`, payload);
  return response.data.data;
};

export const updateReviewStatus = async (id: string, status: string, reviewerId?: string): Promise<ReviewItem> => {
  const response = await apiClient.patch<APIResponse<ReviewItem>>(`/reviews/${id}/status`, {
    status,
    reviewer_id: reviewerId,
  });
  return response.data.data;
};
