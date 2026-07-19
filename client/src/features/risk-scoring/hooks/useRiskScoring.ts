import { useQuery } from '@tanstack/react-query';
import { riskScoringApi, type RiskPrediction, type DistrictRisk, type StationRisk, type RiskSummary } from 'shared/api';

export function useRiskPredictions(limit = 100) {
  return useQuery({
    queryKey: ['risk', 'predictions', limit],
    queryFn: () => riskScoringApi.getPredictions(limit).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useRiskSummary() {
  return useQuery({
    queryKey: ['risk', 'summary'],
    queryFn: () => riskScoringApi.getSummary().then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useDistrictRisk() {
  return useQuery({
    queryKey: ['risk', 'districts'],
    queryFn: () => riskScoringApi.getDistrictRisk().then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useStationRisk() {
  return useQuery({
    queryKey: ['risk', 'stations'],
    queryFn: () => riskScoringApi.getStationRisk().then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useEntityRisk(entityId: string, entityType = 'District') {
  return useQuery({
    queryKey: ['risk', 'entity', entityId, entityType],
    queryFn: () => riskScoringApi.getEntityRisk(entityId, entityType).then((res) => res.data),
    enabled: !!entityId,
    staleTime: 30_000,
  });
}

export type { RiskPrediction, DistrictRisk, StationRisk, RiskSummary };
