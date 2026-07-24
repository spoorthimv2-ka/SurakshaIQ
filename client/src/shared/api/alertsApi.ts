import { apiClient } from 'services/api';

export interface AlertRecord {
  ROWID: string;
  title: string;
  description: string;
  severity: string;
  source: string;
  entity_id?: string;
  entity_type?: string;
  district_id?: string;
  station_id?: string;
  recommended_action?: string;
  status: string;
  CREATEDTIME: string;
  MODIFIEDTIME: string;
}

export interface AlertSummary {
  total_alerts: number;
  active_alerts: number;
  acknowledged_alerts: number;
  resolved_alerts: number;
  critical_alerts: number;
}

export interface AlertFilters {
  status?: string;
  severity?: string;
  district_id?: string;
  station_id?: string;
  limit?: number;
  offset?: number;
}

export const alertsApi = {
  list: (filters?: AlertFilters) =>
    apiClient.get<AlertRecord[]>('/alerts', { params: filters }),

  getSummary: () =>
    apiClient.get<AlertSummary>('/alerts/summary'),

  getActive: (limit = 100, offset = 0, filters?: { district_id?: string; station_id?: string; severity?: string; status?: string }) =>
    apiClient.get<AlertRecord[]>('/alerts/active', { params: { limit, offset, ...filters } }),

  getById: (id: string) =>
    apiClient.get<AlertRecord>(`/alerts/${id}`),

  acknowledge: (id: string) =>
    apiClient.post<AlertRecord>(`/alerts/${id}/acknowledge`, {}),

  resolve: (id: string) =>
    apiClient.post<AlertRecord>(`/alerts/${id}/resolve`, {}),
};
