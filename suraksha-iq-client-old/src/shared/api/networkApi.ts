import apiClient from './client';
import { buildCursorParams } from './pagination';
import type { CursorPaginationParams, PaginatedResponse } from './pagination';

export interface NetworkNode {
  id: string;
  label: string;
  type: string;
}

export interface NetworkEdge {
  source: string;
  target: string;
  weight: number;
}

export interface NetworkGraph {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}

export const networkApi = {
  list: (params?: CursorPaginationParams & Record<string, unknown>) =>
    apiClient.get<PaginatedResponse<NetworkGraph>>('/network-analysis', {
      params: buildCursorParams(params ?? {}),
    }),

  getGraph: (id: string, config?: { signal?: AbortSignal }) =>
    apiClient.get<NetworkGraph>(`/network-analysis/${id}`, config),
};
