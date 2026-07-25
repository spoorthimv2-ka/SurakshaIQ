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
  strength?: number;
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

export interface NetworkFilters {
  crime_category?: string;
  district_id?: string;
  station_id?: string;
  time_period?: string;
  relationship_type?: string;
  risk_level?: string;
  active_investigations?: boolean;
}

export interface AdvancedGraphResponse extends NetworkGraphResponse {
  communities?: Array<{ id: string; label: string; size: number; node_ids: string[]; risk_level: string }>;
  centrality?: Record<string, number>;
}

export interface NetworkAnalyticsResponse {
  community_stats: {
    count: number;
    avg_size: number;
    largest_size: number;
    total_nodes: number;
    total_edges: number;
    density: number;
  };
  central_actors: Array<{ id: string; label: string; score: number; type: string }>;
  most_connected: Array<{ id: string; label: string; connections: number; type: string }>;
  highest_risk_cluster: { id: string; label: string; avg_risk: number; size: number };
  bridge_nodes: Array<{ id: string; label: string; connections: number; type: string }>;
  cluster_summaries: Array<{ id: string; label: string; node_count: number; edge_count: number; risk_level: string }>;
}

export interface NetworkTimelineResponse {
  timeline: Array<{ date: string; timestamp: string; event: string; added_nodes: number; added_edges: number; node_id?: string; crime_type?: string; district_id?: string }>;
  min_date?: string;
  max_date?: string;
}

export interface CommunityDetectionResponse {
  communities: Array<{ id: string; label: string; size: number; node_ids: string[]; edge_count: number; risk_level: string; avg_risk: number; sample_nodes: string[] }>;
  community_count: number;
  modularity: number;
}

export interface CentralActorResponse {
  actors: Array<{ id: string; label: string; score: number; type: string }>;
  metric: string;
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

  getAdvancedGraph: (filters?: NetworkFilters) => {
    const params: Record<string, any> = {};
    if (filters) {
      Object.entries(filters).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== '') params[k] = v; });
    }
    return apiClient.get<AdvancedGraphResponse>('/network/advanced', { params });
  },

  getAnalytics: () =>
    apiClient.get<NetworkAnalyticsResponse>('/network/analytics'),

  getTimeline: () =>
    apiClient.get<NetworkTimelineResponse>('/network/timeline'),

  getCommunities: () =>
    apiClient.get<CommunityDetectionResponse>('/network/communities'),

  getCentralActors: (metric = 'degree') =>
    apiClient.get<CentralActorResponse>('/network/central-actors', { params: { metric } }),

  getBridgeNodes: () =>
    apiClient.get<{ bridge_nodes: any[]; count: number }>('/network/bridge-nodes'),

  advancedSearch: (query: string, limit = 50) =>
    apiClient.get<NetworkSearchResponse>('/network/search/advanced', { params: { q: query, limit } }),
};
