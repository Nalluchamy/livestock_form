import { apiClient } from './api';
import { APIResponse, DatasetInfoData } from '../types';

export const getDatasetInfo = async (): Promise<DatasetInfoData> => {
  const response = await apiClient.get<APIResponse<DatasetInfoData>>('/dataset-info');
  return response.data.data;
};
