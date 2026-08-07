import { apiClient } from './api';
import { GradeRequestPayload, GradeResultData, APIResponse } from '../types';

export const submitGrade = async (payload: GradeRequestPayload): Promise<GradeResultData> => {
  const response = await apiClient.post<APIResponse<GradeResultData>>('/grade', payload);
  return response.data.data;
};
