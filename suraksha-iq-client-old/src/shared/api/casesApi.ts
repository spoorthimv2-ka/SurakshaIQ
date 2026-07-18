import apiClient from './client';
import { buildCursorParams } from './pagination';
import type { CursorPaginationParams, PaginatedResponse } from './pagination';

export interface CaseRecord {
  id: string;
  firNumber: string;
  category: string;
  status: string;
  districtId: string;
  stationId: string;
  registeredAt: string;
  victimName?: string;
  accusedName?: string;
}

export const casesApi = {
  list: (params?: CursorPaginationParams & Record<string, unknown>, config?: { signal?: AbortSignal }) =>
    apiClient.get<PaginatedResponse<CaseRecord>>('/cases', {
      params: buildCursorParams(params ?? {}),
      ...config,
    }),

  getById: (id: string) => apiClient.get<CaseRecord>(`/cases/${id}`),
};
