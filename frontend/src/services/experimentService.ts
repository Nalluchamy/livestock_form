import { apiClient } from './api';
import { APIResponse, ExperimentData } from '../types';

export const getExperiments = async (evaluationType?: string): Promise<{ total: number; experiments: ExperimentData[] }> => {
  const params: Record<string, any> = {};
  if (evaluationType) params.evaluation_type = evaluationType;
  const response = await apiClient.get<APIResponse<{ total: number; experiments: ExperimentData[] }>>('/experiments', { params });
  return response.data.data;
};

export const getLatestExperiment = async (evaluationType?: string): Promise<ExperimentData | null> => {
  const params: Record<string, any> = {};
  if (evaluationType) params.evaluation_type = evaluationType;
  const response = await apiClient.get<APIResponse<ExperimentData | null>>('/experiments/latest', { params });
  return response.data.data;
};

export const runExperiment = async (experimentName = 'retrospective_real_dataset_run', evaluationType = 'retrospective_real'): Promise<any> => {
  const response = await apiClient.post<APIResponse<any>>('/experiments/run', {
    experiment_name: experimentName,
    evaluation_type: evaluationType,
    dataset_version: 'real-v1.0'
  });
  return response.data.data;
};
