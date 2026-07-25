import { useQuery } from '@tanstack/react-query';
import { networkApi, type NetworkGraphResponse, type NetworkStatistics, type NetworkSearchResponse, type AdvancedGraphResponse, type NetworkAnalyticsResponse, type NetworkTimelineResponse, type CommunityDetectionResponse, type CentralActorResponse } from 'shared/api';

export function useNetwork(limit = 500) {
  return useQuery({
    queryKey: ['network', limit],
    queryFn: () => networkApi.getGraph(limit).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useNetworkStatistics() {
  return useQuery({
    queryKey: ['network', 'statistics'],
    queryFn: () => networkApi.getStatistics().then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useOffenderNetwork(offenderId: string) {
  return useQuery({
    queryKey: ['network', 'offender', offenderId],
    queryFn: () => networkApi.getOffenderNetwork(offenderId).then((res) => res.data),
    enabled: !!offenderId,
    staleTime: 30_000,
  });
}

export function useStationNetwork(stationId: string) {
  return useQuery({
    queryKey: ['network', 'station', stationId],
    queryFn: () => networkApi.getStationNetwork(stationId).then((res) => res.data),
    enabled: !!stationId,
    staleTime: 30_000,
  });
}

export function useDistrictNetwork(districtId: string) {
  return useQuery({
    queryKey: ['network', 'district', districtId],
    queryFn: () => networkApi.getDistrictNetwork(districtId).then((res) => res.data),
    enabled: !!districtId,
    staleTime: 30_000,
  });
}

export function useNetworkSearch(query: string, limit = 50) {
  return useQuery({
    queryKey: ['network', 'search', query, limit],
    queryFn: () => networkApi.search(query, limit).then((res) => res.data),
    enabled: query.trim().length > 0,
    staleTime: 30_000,
  });
}

export function useAdvancedNetwork(filters?: {
  crime_category?: string;
  district_id?: string;
  station_id?: string;
  relationship_type?: string;
  risk_level?: string;
  active_investigations?: boolean;
}) {
  return useQuery({
    queryKey: ['network', 'advanced', filters],
    queryFn: () => networkApi.getAdvancedGraph(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useNetworkAnalytics() {
  return useQuery({
    queryKey: ['network', 'analytics'],
    queryFn: () => networkApi.getAnalytics().then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useNetworkTimeline() {
  return useQuery({
    queryKey: ['network', 'timeline'],
    queryFn: () => networkApi.getTimeline().then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useNetworkCommunities() {
  return useQuery({
    queryKey: ['network', 'communities'],
    queryFn: () => networkApi.getCommunities().then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useNetworkCentralActors(metric = 'degree') {
  return useQuery({
    queryKey: ['network', 'central-actors', metric],
    queryFn: () => networkApi.getCentralActors(metric).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useBridgeNodes() {
  return useQuery({
    queryKey: ['network', 'bridge-nodes'],
    queryFn: () => networkApi.getBridgeNodes().then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useAdvancedNetworkSearch(query: string, limit = 50) {
  return useQuery({
    queryKey: ['network', 'search', 'advanced', query, limit],
    queryFn: () => networkApi.advancedSearch(query, limit).then((res) => res.data),
    enabled: query.trim().length > 0,
    staleTime: 30_000,
  });
}

export type {
  NetworkGraphResponse,
  NetworkStatistics,
  NetworkSearchResponse,
  AdvancedGraphResponse,
  NetworkAnalyticsResponse,
  NetworkTimelineResponse,
  CommunityDetectionResponse,
  CentralActorResponse,
};
