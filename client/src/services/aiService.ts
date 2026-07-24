import { apiClient } from './api';

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
}

export interface AISummaryResponse {
  summary: string;
  insights: string[];
  recommendations: Array<{
    title: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
  }>;
  generatedAt: string;
}

export interface AIReportRequest {
  title: string;
  scope: Record<string, unknown>;
  filters: Record<string, unknown>;
}

export interface AIReportResponse {
  reportId: string;
  title: string;
  content: string;
  format: 'text' | 'pdf' | 'json';
  generatedAt: string;
}

class AIService {
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

  async generateRecommendations(payload: Partial<AISummaryRequest>): Promise<AISummaryResponse['recommendations']> {
    try {
      const { data } = await apiClient.post<AISummaryResponse['recommendations']>(`${this.basePath}/recommendations`, payload);
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
      summary: insights.join(' '),
      insights,
      recommendations,
      generatedAt: new Date().toISOString(),
    };
  }

  private fallbackRecommendations(): AISummaryResponse['recommendations'] {
    return [
      { title: 'Increase patrol frequency', description: 'Deploy additional patrols in high-risk areas during peak hours', priority: 'high' },
      { title: 'Deploy additional mobile unit', description: 'Send mobile forensic unit to crime scene for faster evidence collection', priority: 'medium' },
      { title: 'Monitor repeat offender', description: 'Increase surveillance on known repeat offenders in jurisdiction', priority: 'high' },
      { title: 'Increase surveillance', description: 'Install additional CCTV cameras in identified hotspots', priority: 'medium' },
      { title: 'Conduct cyber awareness campaign', description: 'Launch public awareness campaign about online scams and phishing', priority: 'low' },
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

export const aiService = new AIService();
export default aiService;