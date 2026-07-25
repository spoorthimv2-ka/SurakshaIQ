import { apiClient } from 'services/api';

export interface Hotspot {
  id: string;
  district: string;
  police_station: string;
  crime_count: number;
  hotspot_score: number;
  severity: string;
  latest_crime_date?: string;
}

export interface DistrictHotspot {
  district_id: string;
  district_name: string;
  total_crimes: number;
  hotspot_score: number;
  active_firs: number;
  trend: string;
}

export interface StationHotspot {
  station_id: string;
  station_name: string;
  district_id: string;
  district_name: string;
  crime_count: number;
  hotspot_score: number;
  active_firs: number;
}

export interface HotspotSummary {
  total_hotspots: number;
  high_severity_count: number;
  medium_severity_count: number;
  low_severity_count: number;
}

export interface HotspotFilters {
  district_id?: string;
  station_id?: string;
  crime_type?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
}

export const hotspotsApi = {
  list: (filters?: HotspotFilters) =>
    apiClient.get<Hotspot[]>('/hotspots', { params: filters }),

  getDistrictHotspots: (filters?: { start_date?: string; end_date?: string }) =>
    apiClient.get<DistrictHotspot[]>('/hotspots/districts', { params: filters }),

  getStationHotspots: (filters?: { start_date?: string; end_date?: string }) =>
    apiClient.get<StationHotspot[]>('/hotspots/stations', { params: filters }),

  getTopHotspots: (limit = 10, filters?: { start_date?: string; end_date?: string; district_id?: string; station_id?: string; crime_type?: string; status?: string }) =>
    apiClient.get<Hotspot[]>('/hotspots/top', { params: { limit, ...filters } }),
};
