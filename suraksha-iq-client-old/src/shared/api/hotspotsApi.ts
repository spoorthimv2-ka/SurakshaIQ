import apiClient from './client';
import { buildCursorParams } from './pagination';
import type { CursorPaginationParams, PaginatedResponse } from './pagination';

export interface Hotspot {
  id: string;
  name: string;
  districtId: string;
  latitude: number;
  longitude: number;
  intensity: number;
  caseCount: number;
}

export const hotspotsApi = {
  list: (params?: CursorPaginationParams & Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<Hotspot>>('/hotspots', { params: buildCursorParams(params ?? {}) }),

  getById: (id: string, config?: { signal?: AbortSignal }) =>
    apiClient.get<Hotspot>(`/hotspots/${id}`, config),
};
