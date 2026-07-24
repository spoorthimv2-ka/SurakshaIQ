import { apiClient } from 'services/api';

export interface DashboardSummary {
  totalCases: number;
  openCases: number;
  resolvedCases: number;
  activeAlerts: number;
  hotspotsCount: number;
  anomaliesCount: number;
}

export interface DashboardMetric {
  label: string;
  value: number;
  change: number;
  changeType: 'increase' | 'decrease' | 'neutral';
}

export interface SummaryResponse {
  total_crimes: number;
  total_firs: number;
  active_firs: number;
  closed_firs: number;
  crimes_today: number;
  firs_today: number;
  registered_districts: number;
  registered_police_stations: number;
}

export interface RecentCrimeResponse {
  ROWID: string;
  title: string;
  crime_type: string;
  status: string;
  CREATEDTIME: string;
}

export interface RecentFirResponse {
  ROWID: string;
  fir_number: string;
  crime_id: string;
  status: string;
  CREATEDTIME: string;
}

export interface CrimeTrendResponse {
  period: string;
  count: number;
}

export interface DistrictSummaryResponse {
  district_id: string;
  district_name: string;
  crime_count: number;
  fir_count: number;
  active_investigations: number;
}

export interface DashboardFilters {
  jurisdiction?: string;
  districtId?: string;
  policeStation?: string;
  dateRange?: { start?: string; end?: string };
  caseCategory?: string[];
  severity?: string;
  crimeStatus?: string;
  timePreset?: 'today' | 'last7' | 'last30' | 'custom';
}

export const dashboardApi = {
  getSummary: (filters?: DashboardFilters, config?: { signal?: AbortSignal }) =>
    apiClient.get<SummaryResponse>('/dashboard/summary', { params: filters, ...config }),

  getMetrics: (filters?: DashboardFilters, config?: { signal?: AbortSignal }) =>
    apiClient.get<DashboardMetric[]>('/dashboard/metrics', { params: filters, ...config }),

  getDashboardSummary: (filters?: DashboardFilters, config?: { signal?: AbortSignal }) =>
    apiClient.get<SummaryResponse>('/dashboard/summary', { params: filters, ...config }),

  getRecentCrimes: (limit = 10, filters?: DashboardFilters, config?: { signal?: AbortSignal }) =>
    apiClient.get<RecentCrimeResponse[]>('/dashboard/recent-crimes', { params: { limit, ...filters }, ...config }),

  getRecentFirs: (limit = 10, filters?: DashboardFilters, config?: { signal?: AbortSignal }) =>
    apiClient.get<RecentFirResponse[]>('/dashboard/recent-firs', { params: { limit, ...filters }, ...config }),

  getCrimeTrends: (interval = 'daily', filters?: DashboardFilters, config?: { signal?: AbortSignal }) =>
    apiClient.get<CrimeTrendResponse[]>('/dashboard/crime-trends', { params: { interval, ...filters }, ...config }),

  getDistrictSummary: (filters?: DashboardFilters, config?: { signal?: AbortSignal }) =>
    apiClient.get<DistrictSummaryResponse[]>('/dashboard/district-summary', { params: filters, ...config }),
};
