import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { predictiveApi, type PredictiveFilters } from 'shared/api';

export function usePredictiveFilters() {
  const defaultFilters: PredictiveFilters = {
    time_period: '30d',
  };
  return defaultFilters;
}

export function useCrimeForecast(filters?: PredictiveFilters) {
  return useQuery({
    queryKey: ['predictive', 'forecast', filters],
    queryFn: () => predictiveApi.getForecast(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useEmergingHotspots(filters?: PredictiveFilters) {
  return useQuery({
    queryKey: ['predictive', 'emerging-hotspots', filters],
    queryFn: () => predictiveApi.getEmergingHotspots(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useDynamicRiskIndex(filters?: PredictiveFilters) {
  return useQuery({
    queryKey: ['predictive', 'risk-index', filters],
    queryFn: () => predictiveApi.getRiskIndex(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function usePatrolRecommendations(filters?: PredictiveFilters) {
  return useQuery({
    queryKey: ['predictive', 'patrol-recommendations', filters],
    queryFn: () => predictiveApi.getPatrolRecommendations(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useTemporalIntelligence(filters?: PredictiveFilters) {
  return useQuery({
    queryKey: ['predictive', 'temporal-intelligence', filters],
    queryFn: () => predictiveApi.getTemporalIntelligence(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useTrendAnalysis(filters?: PredictiveFilters) {
  return useQuery({
    queryKey: ['predictive', 'trend-analysis', filters],
    queryFn: () => predictiveApi.getTrendAnalysis(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useScenarioSimulation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (scenario: any) => predictiveApi.simulateScenario(scenario).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['predictive'] });
    },
  });
}

export function usePredictiveDashboard(filters?: PredictiveFilters) {
  return useQuery({
    queryKey: ['predictive', 'dashboard', filters],
    queryFn: () => predictiveApi.getPredictiveDashboard(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function usePredictiveAiIntelligence(filters?: PredictiveFilters) {
  return useQuery({
    queryKey: ['predictive', 'ai-intelligence', filters],
    queryFn: () => predictiveApi.getAiIntelligence(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}
