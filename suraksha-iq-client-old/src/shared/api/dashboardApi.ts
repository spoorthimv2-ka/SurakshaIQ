import apiClient from './client';

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

export const dashboardApi = {
  getSummary: (params?: Record<string, unknown>, config?: { signal?: AbortSignal }) =>
    apiClient.get<DashboardSummary>('/dashboard/summary', { params, ...config }),

  getMetrics: (params?: Record<string, unknown>, config?: { signal?: AbortSignal }) =>
    apiClient.get<DashboardMetric[]>('/dashboard/metrics', { params, ...config }),
};
