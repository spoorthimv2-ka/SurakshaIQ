import apiClient from './client';
import { buildCursorParams } from './pagination';
import type { CursorPaginationParams, PaginatedResponse } from './pagination';

export interface RepeatOffender {
  id: string;
  alias: string;
  caseCount: number;
  lastSeen: string;
  districtId: string;
}

export const repeatOffendersApi = {
  list: (params?: CursorPaginationParams & Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<RepeatOffender>>('/repeat-offenders', {
      params: buildCursorParams(params ?? {}),
    }),
};
