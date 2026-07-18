import apiClient from './client';
import { buildCursorParams } from './pagination';
import type { CursorPaginationParams, PaginatedResponse } from './pagination';

export interface RiskScore {
  id: string;
  entityId: string;
  entityType: string;
  score: number;
  factors: string[];
  updatedAt: string;
}

export const riskScoringApi = {
  list: (params?: CursorPaginationParams & Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<RiskScore>>('/risk-scoring', {
      params: buildCursorParams(params ?? {}),
    }),
};
