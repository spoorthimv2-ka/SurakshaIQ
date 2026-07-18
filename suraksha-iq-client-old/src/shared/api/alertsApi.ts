import apiClient from './client';
import { buildCursorParams } from './pagination';
import type { CursorPaginationParams, PaginatedResponse } from './pagination';

export interface AlertRecord {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  createdAt: string;
  acknowledged: boolean;
}

export const alertsApi = {
  list: (params?: CursorPaginationParams & Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<AlertRecord>>('/alerts', { params: buildCursorParams(params ?? {}) }),

  getById: (id: string) => apiClient.get<AlertRecord>(`/alerts/${id}`),

  acknowledge: (id: string) => apiClient.put<AlertRecord>(`/alerts/${id}/acknowledge`, {}),
};
