import apiClient from './client';
import { buildCursorParams } from './pagination';
import type { CursorPaginationParams, PaginatedResponse } from './pagination';

export interface Report {
  id: string;
  name: string;
  type: 'custom' | 'scheduled';
  status: 'pending' | 'ready' | 'failed';
  createdAt: string;
}

export const reportsApi = {
  list: (params?: CursorPaginationParams & Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Report>>('/reports', { params: buildCursorParams(params ?? {}) }),

  generate: (data: { name: string; filters: Record<string, unknown> }) =>
    apiClient.post<Report>('/reports/generate', data),

  export: (id: string, format: 'pdf' | 'xlsx') =>
    apiClient.get<Blob>(`/reports/${id}/export`, { params: { format }, responseType: 'blob' }),
};
