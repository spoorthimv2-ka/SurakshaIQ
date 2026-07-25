import { apiClient } from 'services/api';

export interface PredictiveFilters {
  district_id?: string;
  station_id?: string;
  crime_category?: string;
  time_period?: string;
  start_date?: string;
  end_date?: string;
}

export interface ForecastPoint {
  date: string;
  predicted_count: number;
  confidence_low: number;
  confidence_high: number;
  confidence_score: number;
}

export interface CrimeForecast {
  entity_id: string;
  entity_type: string;
  entity_name: string;
  period: string;
  forecast_points: ForecastPoint[];
  confidence: number;
  total_predicted: number;
}

export interface EmergingHotspot {
  id: string;
  district_id: string;
  district_name: string;
  station_id: string;
  station_name: string;
  intensity: number;
  confidence: number;
  risk_level: string;
  explanation: string;
  predicted_crime_count: number;
  latitude?: number;
  longitude?: number;
}

export interface RiskIndex {
  entity_id: string;
  entity_type: string;
  entity_name: string;
  risk_score: number;
  risk_level: string;
  trend: string;
  previous_score: number;
  score_change: number;
  explanation: string;
}

export interface PatrolRecommendation {
  zone_id: string;
  zone_name: string;
  zone_type: string;
  recommendation_type: string;
  priority: string;
  description: string;
  reason: string;
  suggested_patrols: number;
  time_windows: string[];
}

export interface TemporalDistribution {
  hour?: number;
  day_of_week?: string;
  month?: string;
  season?: string;
  count: number;
  percentage: number;
}

export interface TemporalIntelligence {
  hourly_distribution: TemporalDistribution[];
  daily_distribution: TemporalDistribution[];
  monthly_distribution: TemporalDistribution[];
  seasonal_distribution: TemporalDistribution[];
  peak_hour?: number;
  peak_day?: string;
  peak_month?: string;
  peak_season?: string;
}

export interface TrendCategory {
  category: string;
  trend: string;
  change_percent: number;
  count_current: number;
  count_previous: number;
}

export interface EmergingPattern {
  pattern_type: string;
  description: string;
  affected_entities: string[];
  confidence: number;
  severity: string;
}

export interface TrendAnalysis {
  increasing_categories: TrendCategory[];
  decreasing_categories: TrendCategory[];
  stable_categories: TrendCategory[];
  emerging_patterns: EmergingPattern[];
  overall_trend: string;
}

export interface ScenarioFilters {
  district_id?: string;
  station_id?: string;
  crime_category?: string;
  time_window?: string;
}

export interface ScenarioSimulation {
  filters: ScenarioFilters;
  forecast: Record<string, any>;
  risk: Record<string, any>;
  hotspots: Record<string, any>[];
  patrol_recommendations: Record<string, any>[];
}

export interface PredictiveDashboard {
  highest_risk_district: Record<string, any>;
  fastest_growing_crime: Record<string, any>;
  emerging_hotspot: Record<string, any>;
  forecast_confidence: number;
  recommended_patrol_increase: number;
  predicted_incident_count: number;
  time_period: string;
}

export interface PredictiveAIExplanation {
  forecast_explanation: string;
  risk_explanation: string;
  strategy_recommendations: string[];
  executive_summary: string;
  confidence: number;
  is_fallback: boolean;
}

export const predictiveApi = {
  getForecast: (filters?: PredictiveFilters) =>
    apiClient.get<CrimeForecast[]>('/predictive/forecast', { params: filters }),

  getEmergingHotspots: (filters?: PredictiveFilters) =>
    apiClient.get<EmergingHotspot[]>('/predictive/emerging-hotspots', { params: filters }),

  getRiskIndex: (filters?: PredictiveFilters) =>
    apiClient.get<RiskIndex[]>('/predictive/risk-index', { params: filters }),

  getPatrolRecommendations: (filters?: PredictiveFilters) =>
    apiClient.get<PatrolRecommendation[]>('/predictive/patrol-recommendations', { params: filters }),

  getTemporalIntelligence: (filters?: PredictiveFilters) =>
    apiClient.get<TemporalIntelligence>('/predictive/temporal-intelligence', { params: filters }),

  getTrendAnalysis: (filters?: PredictiveFilters) =>
    apiClient.get<TrendAnalysis>('/predictive/trend-analysis', { params: filters }),

  simulateScenario: (scenario: ScenarioFilters) =>
    apiClient.post<ScenarioSimulation>('/predictive/scenario-simulator', scenario),

  getPredictiveDashboard: (filters?: PredictiveFilters) =>
    apiClient.get<PredictiveDashboard>('/predictive/dashboard', { params: filters }),

  getAiIntelligence: (filters?: PredictiveFilters) =>
    apiClient.post<PredictiveAIExplanation>('/predictive/ai-intelligence', { filters }),
};
