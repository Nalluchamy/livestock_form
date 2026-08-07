import { apiClient } from './api';
import { GradingEventHistoryResponse, SingleGradingEventDetail, APIResponse } from '../types';

export const getGradingHistory = async (skip = 0, limit = 50): Promise<GradingEventHistoryResponse> => {
  const response = await apiClient.get<APIResponse<GradingEventHistoryResponse>>(
    `/grading-events?skip=${skip}&limit=${limit}`
  );
  return response.data.data;
};

export const getGradingEventById = async (id: string): Promise<SingleGradingEventDetail> => {
  const response = await apiClient.get<APIResponse<SingleGradingEventDetail>>(`/grading-events/${id}`);
  return response.data.data;
};
