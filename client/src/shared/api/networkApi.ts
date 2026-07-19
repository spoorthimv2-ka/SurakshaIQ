import { apiClient } from 'services/api';

export interface NetworkNode {
  id: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
}

export interface NetworkEdge {
  source: string;
  target: string;
  type?: string;
  properties?: Record<string, any>;
}

export interface NetworkStatistics {
  total_nodes: number;
  total_edges: number;
  connected_offenders: number;
  connected_stations: number;
  connected_districts: number;
  average_connections: number;
}

export interface NetworkGraphResponse {
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  statistics: NetworkStatistics;
  metadata?: Record<string, any>;
}

export interface NetworkSearchResponse {
  query: string;
  nodes: NetworkNode[];
  edges: NetworkEdge[];
}

export const networkApi = {
  getGraph: (limit = 500) =>
    apiClient.get<NetworkGraphResponse>('/network', { params: { limit } }),

  getStatistics: () =>
    apiClient.get<NetworkStatistics>('/network/statistics'),

  getOffenderNetwork: (offenderId: string) =>
    apiClient.get<NetworkGraphResponse>(`/network/offenders/${offenderId}`),

  getStationNetwork: (stationId: string) =>
    apiClient.get<NetworkGraphResponse>(`/network/stations/${stationId}`),

  getDistrictNetwork: (districtId: string) =>
    apiClient.get<NetworkGraphResponse>(`/network/districts/${districtId}`),

  search: (query: string, limit = 50) =>
    apiClient.get<NetworkSearchResponse>('/network/search', { params: { q: query, limit } }),
};
