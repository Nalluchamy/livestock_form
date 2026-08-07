import { apiClient } from './api';
import { DisagreementRequestPayload, APIResponse } from '../types';

export const submitDisagreement = async (payload: DisagreementRequestPayload): Promise<any> => {
  const response = await apiClient.post<APIResponse<any>>('/disagreements', payload);
  return response.data.data;
};
