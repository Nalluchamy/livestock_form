import { apiClient } from './api';
import { MetricsData, AgreementMetricsData, APIResponse } from '../types';

export const getMetrics = async (): Promise<MetricsData> => {
  const response = await apiClient.get<APIResponse<MetricsData>>('/metrics');
  return response.data.data;
};

export const getAgreementMetrics = async (): Promise<AgreementMetricsData> => {
  const response = await apiClient.get<APIResponse<AgreementMetricsData>>('/metrics/agreement');
  return response.data.data;
};

