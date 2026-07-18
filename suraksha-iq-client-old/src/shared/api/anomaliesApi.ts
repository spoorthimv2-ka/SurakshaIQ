import apiClient from './client';
import { buildCursorParams } from './pagination';
import type { CursorPaginationParams, PaginatedResponse } from './pagination';

export interface Anomaly {
  id: string;
  title: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  detectedAt: string;
  districtId: string;
}

export const anomaliesApi = {
  list: (params?: CursorPaginationParams & Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Anomaly>>('/anomalies', { params: buildCursorParams(params ?? {}) }),
};
