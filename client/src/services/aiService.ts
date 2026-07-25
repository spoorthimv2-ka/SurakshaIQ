import { apiClient } from './api';
import { useMutation, useQueryClient } from '@tanstack/react-query';

// ============================================================
// Request / Response types
// ============================================================

export interface AISummaryRequest {
  metrics: {
    total_crimes: number;
    active_firs: number;
    closed_firs: number;
    detection_rate: number;
    hotspots_count: number;
    trends: Array<{ period: string; count: number }>;
  };
  hotspots: Array<{ location: string; riskLevel: string; change: number }>;
  anomalies?: Array<{ title: string; severity: string }>;
  networks?: Array<{ id: string; type: string }>;
  filters?: Record<string, unknown>;
  intelligence_scope?: Record<string, unknown>;
  dashboard_payload?: Record<string, unknown>;
}

export interface AISummaryResponse {
  overallRisk: string;
  executiveSummary: string;
  keyFindings: string[];
  recommendedActions: string[];
  confidence: number;
  generatedAt: string;
  isFallback: boolean;
  analyticsUsed?: string[];
  model?: string | null;
}

export interface AIReportRequest {
  title: string;
  scope: Record<string, unknown>;
  filters: Record<string, unknown>;
  report_type?: string;
  analytics?: Record<string, unknown>;
}

export interface AIReportResponse {
  reportId: string;
  title: string;
  content: string;
  format: 'text' | 'pdf' | 'json';
  generatedAt: string;
  isFallback?: boolean;
  analyticsUsed?: string[];
  model?: string | null;
  confidence?: number;
  sections?: Array<{ title: string; content: string }>;
}

export interface AIChatRequest {
  message: string;
  context?: Record<string, unknown>;
}

export interface AIChatResponse {
  response: string;
  confidence: number;
  analyticsUsed: string[];
  isFallback: boolean;
  model?: string | null;
  generatedAt: string;
}

export interface AIFirIntelligenceRequest {
  fir_number?: string;
  description: string;
  sections?: string;
  victim_name?: string;
  suspect_name?: string;
  district_id?: string;
  station_id?: string;
  status?: string;
  title?: string;
}

export interface AIFirIntelligenceResponse {
  crime_category: string;
  severity: string;
  modus_operandi: string;
  entities: Record<string, string[]>;
  investigation_suggestions: string[];
  confidence: number;
  generatedAt: string;
  isFallback: boolean;
  analyticsUsed?: string[];
  model?: string | null;
}

export interface AIPatternRequest {
  analytics: Record<string, unknown>;
}

export interface AIPatternResponse {
  patterns: Array<Record<string, unknown>>;
  correlations: Array<Record<string, unknown>>;
  confidence: number;
  generatedAt: string;
  isFallback: boolean;
  analyticsUsed?: string[];
  model?: string | null;
}

export interface AIRecommendationRequest {
  analytics: Record<string, unknown>;
}

export interface AIRecommendationResponse {
  recommendations: Array<{ title: string; description: string; priority: string; category: string }>;
  overall_risk: string;
  confidence: number;
  generatedAt: string;
  isFallback: boolean;
  analyticsUsed?: string[];
  model?: string | null;
}

export interface AIExplainRequest {
  chart_type: string;
  data: Record<string, unknown>;
  filters: Record<string, unknown>;
}

export interface AIExplainResponse {
  explanation: string;
  confidence: number;
  generatedAt: string;
  isFallback: boolean;
  analyticsUsed?: string[];
  model?: string | null;
}

export interface AIEvidenceSummaryRequest {
  document_type: string;
  content: string;
}

export interface AIEvidenceSummaryResponse {
  summary: string;
  extracted_entities: Record<string, string[]>;
  key_points: string[];
  confidence: number;
  generatedAt: string;
  isFallback: boolean;
  analyticsUsed?: string[];
  model?: string | null;
}

export interface AITimelineRequest {
  incident_description: string;
}

export interface AITimelineResponse {
  events: Array<Record<string, unknown>>;
  narrative: string;
  confidence: number;
  generatedAt: string;
  isFallback: boolean;
  analyticsUsed?: string[];
  model?: string | null;
}

// ============================================================
// Legacy service class (kept for backward compatibility)
// ============================================================

class AIServiceLegacy {
  private basePath = '/ai';

  async generateSummary(payload: AISummaryRequest): Promise<AISummaryResponse> {
    try {
      const { data } = await apiClient.post<AISummaryResponse>(`${this.basePath}/summary`, payload);
      return data;
    } catch (error) {
      console.warn('[AI Service] Summary generation failed, using fallback', error);
      return this.fallbackSummary(payload);
    }
  }

  async generateRecommendations(payload: Partial<AISummaryRequest>): Promise<string[]> {
    try {
      const { data } = await apiClient.post<string[]>(`${this.basePath}/recommendations`, payload);
      return data;
    } catch (error) {
      console.warn('[AI Service] Recommendations failed, using fallback', error);
      return this.fallbackRecommendations();
    }
  }

  async generateReport(payload: AIReportRequest): Promise<AIReportResponse> {
    try {
      const { data } = await apiClient.post<AIReportResponse>(`${this.basePath}/report`, payload);
      return data;
    } catch (error) {
      console.warn('[AI Service] Report generation failed', error);
      throw new Error('Failed to generate report');
    }
  }

  async chat(message: string, context?: Record<string, unknown>): Promise<{ response: string }> {
    try {
      const { data } = await apiClient.post<{ response: string }>(`${this.basePath}/chat`, {
        message,
        context,
      });
      return data;
    } catch (error) {
      console.warn('[AI Service] Chat failed, using fallback', error);
      return { response: this.fallbackChatResponse(message) };
    }
  }

  private fallbackSummary(payload: AISummaryRequest): AISummaryResponse {
    const insights: string[] = [];
    const { metrics, hotspots } = payload;

    if (metrics.trends.length > 1) {
      const first = metrics.trends[0].count;
      const last = metrics.trends[metrics.trends.length - 1].count;
      const change = ((last - first) / Math.max(first, 1)) * 100;
      insights.push(
        change > 0
          ? `Crime incidents increased ${change.toFixed(1)}% over the selected period.`
          : `Crime incidents decreased ${Math.abs(change).toFixed(1)}% over the selected period.`
      );
    }

    if (hotspots.length > 0) {
      insights.push(`${hotspots.filter(h => h.riskLevel === 'critical' || h.riskLevel === 'high').length} high-risk hotspots identified.`);
    }

    if (metrics.detection_rate < 50) {
      insights.push('Detection rate is below 50%. Recommend reviewing investigation procedures.');
    }

    const recommendations = this.fallbackRecommendations();

    return {
      overallRisk: metrics.detection_rate < 50 ? 'High' : 'Medium',
      executiveSummary: insights.join(' '),
      keyFindings: insights,
      recommendedActions: recommendations,
      confidence: 0.75,
      generatedAt: new Date().toISOString(),
      isFallback: true,
    };
  }

  private fallbackRecommendations(): string[] {
    return [
      'Increase patrol frequency: Deploy additional patrols in high-risk areas during peak hours',
      'Deploy additional mobile unit: Send mobile forensic unit to crime scene for faster evidence collection',
      'Monitor repeat offender: Increase surveillance on known repeat offenders in jurisdiction',
      'Increase surveillance: Install additional CCTV cameras in identified hotspots',
      'Conduct cyber awareness campaign: Launch public awareness campaign about online scams and phishing',
    ];
  }

  private fallbackChatResponse(message: string): string {
    const lower = message.toLowerCase();
    if (lower.includes('hotspot')) return 'Key hotspots are concentrated in urban areas. Consider increasing patrols near MG Road and City Market.';
    if (lower.includes('trend')) return 'Crime incidents show a seasonal pattern with peaks in summer months. Theft and burglary are the most reported categories.';
    if (lower.includes('district')) return 'Bangalore Urban requires immediate attention due to high incident volume. Mysuru and Belagavi show emerging trends.';
    if (lower.includes('anomal')) return 'Current anomalies include a burglary spike in North Bangalore and increased cybercrime reports.';
    return 'I can help you analyze crime data, identify hotspots, and provide operational recommendations. Try asking about specific districts, crime types, or trends.';
  }
}

export const aiService = new AIServiceLegacy();
export default aiService;

// ============================================================
// React Query hooks
// ============================================================

export function useAiSummary() {
  return useMutation({
    mutationFn: (payload: AISummaryRequest) =>
      apiClient.post<AISummaryResponse>('/ai/summary', payload).then((res) => res.data),
  });
}

export function useAiChat() {
  return useMutation({
    mutationFn: (payload: AIChatRequest) =>
      apiClient.post<AIChatResponse>('/ai/chat', payload).then((res) => res.data),
  });
}

export function useAiFirIntelligence() {
  return useMutation({
    mutationFn: (payload: AIFirIntelligenceRequest) =>
      apiClient.post<AIFirIntelligenceResponse>('/ai/fir-intelligence', payload).then((res) => res.data),
  });
}

export function useAiPatterns() {
  return useMutation({
    mutationFn: (payload: AIPatternRequest) =>
      apiClient.post<AIPatternResponse>('/ai/patterns', payload).then((res) => res.data),
  });
}

export function useAiRecommendations() {
  return useMutation({
    mutationFn: (payload: AIRecommendationRequest) =>
      apiClient.post<AIRecommendationResponse>('/ai/recommendations', payload).then((res) => res.data),
  });
}

export function useAiReport() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: AIReportRequest) =>
      apiClient.post<AIReportResponse>('/ai/report', payload).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai'] });
    },
  });
}

export function useAiExplain() {
  return useMutation({
    mutationFn: (payload: AIExplainRequest) =>
      apiClient.post<AIExplainResponse>('/ai/explain', payload).then((res) => res.data),
  });
}

export function useAiEvidenceSummary() {
  return useMutation({
    mutationFn: (payload: AIEvidenceSummaryRequest) =>
      apiClient.post<AIEvidenceSummaryResponse>('/ai/evidence-summary', payload).then((res) => res.data),
  });
}

export function useAiTimeline() {
  return useMutation({
    mutationFn: (payload: AITimelineRequest) =>
      apiClient.post<AITimelineResponse>('/ai/timeline', payload).then((res) => res.data),
  });
}
