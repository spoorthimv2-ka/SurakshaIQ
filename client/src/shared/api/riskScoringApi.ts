import { apiClient } from 'services/api';

export interface RiskFactor {
  name: string;
  weight: number;
  contribution: number;
}

export interface RiskPrediction {
  entity_id: string;
  entity_type: string;
  entity_name: string;
  risk_score: number;
  risk_level: string;
  contributing_factors: RiskFactor[];
  last_updated: string;
}

export interface DistrictRisk {
  district_id: string;
  district_name: string;
  risk_score: number;
  risk_level: string;
  crime_count: number;
  fir_count: number;
  hotspot_score: number;
  repeat_offender_count: number;
  contributing_factors: RiskFactor[];
}

export interface StationRisk {
  station_id: string;
  station_name: string;
  district_id: string;
  district_name: string;
  risk_score: number;
  risk_level: string;
  crime_count: number;
  fir_count: number;
  hotspot_score: number;
  contributing_factors: RiskFactor[];
}

export interface RiskSummary {
  total_entities: number;
  average_risk: number;
  highest_risk_district: string;
  highest_risk_station: string;
  total_high_risk: number;
  total_critical_risk: number;
  risk_distribution: Array<{
    entity_id: string;
    entity_type: string;
    entity_name: string;
    risk_score: number;
    risk_level: string;
  }>;
}

export const riskScoringApi = {
  getPredictions: (limit = 100) =>
    apiClient.get<RiskPrediction[]>('/predictive-risk', { params: { limit } }),

  getSummary: () =>
    apiClient.get<RiskSummary>('/predictive-risk/summary'),

  getDistrictRisk: () =>
    apiClient.get<DistrictRisk[]>('/predictive-risk/districts'),

  getStationRisk: () =>
    apiClient.get<StationRisk[]>('/predictive-risk/stations'),

  getEntityRisk: (entityId: string, entityType = 'District') =>
    apiClient.get<RiskPrediction>('/predictive-risk/' + entityId, { params: { entity_type: entityType } }),
};
