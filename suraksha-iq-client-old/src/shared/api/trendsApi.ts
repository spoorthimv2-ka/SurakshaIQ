import apiClient from './client';
import { buildCursorParams } from './pagination';
import type { CursorPaginationParams, PaginatedResponse } from './pagination';

export interface TrendPoint {
  date: string;
  value: number;
  category: string;
}

export const trendsApi = {
  list: (params?: CursorPaginationParams & Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<TrendPoint>>('/trends', { params: buildCursorParams(params ?? {}) }),

  forecast: (params?: Record<string, unknown>, config?: { signal?: AbortSignal }) =>
    apiClient.get<TrendPoint[]>('/trends/forecast', { params, ...config }),
};
