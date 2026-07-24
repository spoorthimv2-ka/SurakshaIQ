import { useQuery } from '@tanstack/react-query';
import { dashboardApi, type SummaryResponse, type RecentCrimeResponse, type RecentFirResponse, type CrimeTrendResponse, type DistrictSummaryResponse, type DashboardFilters } from 'shared/api';

export function useDashboardSummary(filters?: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard', 'summary', filters],
    queryFn: () => dashboardApi.getDashboardSummary(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useRecentCrimes(limit = 10, filters?: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard', 'recent-crimes', limit, filters],
    queryFn: () => dashboardApi.getRecentCrimes(limit, filters).then((res) => res.data),
    staleTime: 30_000,
  });
}

export function useRecentFirs(limit = 10, filters?: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard', 'recent-firs', limit, filters],
    queryFn: () => dashboardApi.getRecentFirs(limit, filters).then((res) => res.data),
    staleTime: 30_000,
  });
}

export function useCrimeTrends(interval = 'daily', filters?: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard', 'crime-trends', interval, filters],
    queryFn: () => dashboardApi.getCrimeTrends(interval, filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useDistrictSummary(filters?: DashboardFilters) {
  return useQuery({
    queryKey: ['dashboard', 'district-summary', filters],
    queryFn: () => dashboardApi.getDistrictSummary(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export type { SummaryResponse, RecentCrimeResponse, RecentFirResponse, CrimeTrendResponse, DistrictSummaryResponse, DashboardFilters };