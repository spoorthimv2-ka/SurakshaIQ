import apiClient from './client';

export interface DistrictSummary {
  id: string;
  name: string;
  caseCount: number;
  riskIndex: number;
}

export const districtsApi = {
  list: () => apiClient.get<DistrictSummary[]>('/districts'),

  getById: (districtId: string) => apiClient.get<DistrictSummary>(`/districts/${districtId}`),
};
