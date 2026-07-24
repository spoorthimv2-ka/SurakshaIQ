import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { FileText, MapPin, FileCheck, ShieldAlert, ClipboardList, Users, Map, BarChart2, Bell, Eye, Video, Megaphone, Search, Activity } from 'lucide-react';
import { KpiCard, Card, AlertBanner, DataTable, LoadingSkeleton, EmptyState } from 'shared/components';
import { useDashboardSummary, useRecentCrimes, useRecentFirs, useCrimeTrends } from 'features/dashboard/hooks/useDashboard';
import { useHotspots } from 'features/hotspots/hooks/useHotspots';
import { useAnomalies } from 'features/anomalies/hooks/useAnomalies';
import { useFilterStore } from 'shared/state';
import OperationalStatus from 'shared/components/operational-status/OperationalStatus';
import IntelligenceScope from 'shared/components/intelligence-scope/IntelligenceScope';
import AIExecutiveSummary, { type ExecutiveBriefing } from 'shared/components/ai-executive-summary/AIExecutiveSummary';
import LiveIntelligenceFeed from 'shared/components/live-intelligence-feed/LiveIntelligenceFeed';
import HotspotSnapshot from 'shared/components/hotspot-snapshot/HotspotSnapshot';
import TrendIntelligence from 'shared/components/trend-intelligence/TrendIntelligence';
import ResourceRecommendations from 'shared/components/resource-recommendations/ResourceRecommendations';
import EmergingAlerts from 'shared/components/emerging-alerts/EmergingAlerts';
import QuickActions from 'shared/components/quick-actions/QuickActions';
import AIAssistant from 'shared/components/ai-assistant/AIAssistant';
import { alertsApi } from 'shared/api/alertsApi';
import { aiService } from 'services/aiService';

const DETECTION_RATE_MOCK = 68.5;

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const store = useFilterStore();

  const filters = useMemo(() => {
    const params: Record<string, unknown> = {};
    if (store.jurisdiction) params.jurisdiction = store.jurisdiction;
    if (store.policeStation) params.policeStation = store.policeStation;
    if (store.dateRange?.start) params.startDate = store.dateRange.start;
    if (store.dateRange?.end) params.endDate = store.dateRange.end;
    if (store.caseCategory && store.caseCategory.length > 0) params.caseCategory = store.caseCategory.join(',');
    if (store.severity) params.severity = store.severity;
    if (store.crimeStatus) params.crimeStatus = store.crimeStatus;
    if (store.timePreset) params.timePreset = store.timePreset;
    return params;
  }, [store.jurisdiction, store.policeStation, store.dateRange, store.caseCategory, store.severity, store.crimeStatus, store.timePreset]);

  const { data: summary, error: summaryError, refetch: refetchSummary } = useDashboardSummary(filters);
  const { data: trends, refetch: refetchTrends } = useCrimeTrends('daily', filters);
  const { data: recentCrimes, isLoading: crimesLoading, refetch: refetchCrimes } = useRecentCrimes(10, filters);
  const { data: recentFirs, isLoading: firsLoading, refetch: refetchFirs } = useRecentFirs(10, filters);
  const { data: hotspots } = useHotspots({ limit: 20, ...filters });
  const { data: anomalies } = useAnomalies(20);

  const [aiBriefing, setAiBriefing] = useState<ExecutiveBriefing | null>(null);
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [aiError, setAiError] = useState(false);

  if (summaryError) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Command Overview</h1>
          <p className="text-sm text-gov-slate">Welcome back</p>
        </div>
        <AlertBanner variant="error" title="Failed to load dashboard" message="Unable to fetch dashboard metrics. Please try again later." />
      </div>
    );
  }

  const totalProcessed = (summary?.active_firs ?? 0) + (summary?.closed_firs ?? 0);
  const detectionRate = totalProcessed > 0 ? Math.min(((summary?.closed_firs ?? 0) / totalProcessed) * 100, 100) : DETECTION_RATE_MOCK;

  const refreshAi = useCallback(async () => {
    setIsAiLoading(true);
    setAiError(false);
    try {
      const result = await aiService.generateSummary({
        metrics: {
          total_crimes: summary?.total_crimes ?? 0,
          active_firs: summary?.active_firs ?? 0,
          closed_firs: summary?.closed_firs ?? 0,
          detection_rate: detectionRate,
          hotspots_count: hotspots?.length ?? 0,
          trends: (trends ?? []).map((t) => ({ period: t.period, count: t.count })),
        },
        hotspots: (hotspots ?? []).map((h) => ({
          location: h.district ?? 'Unknown',
          riskLevel: h.severity?.toLowerCase() ?? 'medium',
          change: 0,
        })),
        anomalies: (anomalies ?? []).map((a) => ({
          title: (a as any).title ?? (a as any).anomaly_type ?? 'Unknown',
          severity: (a as any).severity ?? 'medium',
        })),
      });
      setAiBriefing(result);
    } catch (error) {
      console.warn('AI summary load failed', error);
      setAiError(true);
    } finally {
      setIsAiLoading(false);
    }
  }, [summary, detectionRate, trends, hotspots, anomalies]);

  useEffect(() => {
    refreshAi();
  }, [refreshAi]);

  const refreshAll = useCallback(async () => {
    await Promise.all([
      refetchSummary(),
      refetchTrends(),
      refetchCrimes(),
      refetchFirs(),
      refreshAi(),
    ]);
  }, [refetchSummary, refetchTrends, refetchCrimes, refetchFirs, refreshAi]);

  const handleApplyFilters = useCallback(async () => {
    await refreshAll();
  }, [refreshAll]);

  const handleResetFilters = useCallback(async () => {
    store.resetFilters();
    await refreshAll();
  }, [store, refreshAll]);

  const alertFilters = useMemo(() => ({
    limit: 20,
    ...(store.jurisdiction ? { district_id: store.jurisdiction } : {}),
    ...(store.severity ? { severity: store.severity } : {}),
  }), [store.jurisdiction, store.severity]);

  const hotspotFilters = useMemo(() => ({
    ...(store.jurisdiction ? { district_id: store.jurisdiction } : {}),
    ...(store.policeStation ? { station_id: store.policeStation } : {}),
    ...(store.dateRange?.start ? { start_date: store.dateRange.start } : {}),
    ...(store.dateRange?.end ? { end_date: store.dateRange.end } : {}),
    limit: 10,
  }), [store.jurisdiction, store.policeStation, store.dateRange?.start, store.dateRange?.end]);

  const { data: hotspotsData } = useHotspots(hotspotFilters);

  const snapshotHotspots = useMemo(() => {
    const severityMap: Record<string, 'critical' | 'high' | 'medium' | 'low'> = {
      CRITICAL: 'critical',
      HIGH: 'high',
      MEDIUM: 'medium',
      LOW: 'low',
    };
    return (hotspotsData ?? []).slice(0, 5).map((h, idx) => ({
      rank: idx + 1,
      location: h.district,
      riskLevel: severityMap[h.severity?.toUpperCase() ?? 'LOW'] ?? 'medium',
      change: 0,
    }));
  }, [hotspotsData]);

  const { data: alertsData } = useQuery({
    queryKey: ['alerts', 'active', store.jurisdiction, store.severity, store.crimeStatus],
    queryFn: () => alertsApi.getActive(alertFilters.limit ?? 20, 0, alertFilters).then((res) => res.data),
    staleTime: 30_000,
  });

  const liveFeedItems = useMemo(() => (alertsData ?? []).map((a) => ({
    id: a.ROWID,
    severity: (a.severity?.toLowerCase() as any) ?? 'medium',
    time: a.CREATEDTIME ? new Date(a.CREATEDTIME).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--',
    location: a.district_id ?? a.station_id ?? 'Unknown',
    description: a.title,
  })), [alertsData]);

  const emergingAlertItems = useMemo(() => (alertsData ?? []).map((a) => ({
    id: a.ROWID,
    title: a.title,
    location: a.district_id ?? a.station_id ?? 'Unknown',
    time: a.CREATEDTIME ? new Date(a.CREATEDTIME).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--',
    severity: (a.severity?.toLowerCase() as any) ?? 'medium',
    suggestedAction: a.recommended_action ?? 'Review and take appropriate action',
  })), [alertsData]);

  const mockResourceRecommendations = useMemo(() => {
    const source = aiBriefing?.recommendedActions ?? [];
    if (!source.length) {
      return [
        { id: "1", title: "Increase patrol frequency", description: "Deploy additional patrols in high-risk areas during peak hours", priority: "high" as const, icon: Users },
        { id: "2", title: "Deploy additional mobile unit", description: "Send mobile forensic unit to crime scene for faster evidence collection", priority: "medium" as const, icon: MapPin },
        { id: "3", title: "Monitor repeat offender", description: "Increase surveillance on known repeat offenders in jurisdiction", priority: "high" as const, icon: Eye },
        { id: "4", title: "Increase surveillance", description: "Install additional CCTV cameras in identified hotspots", priority: "medium" as const, icon: Video },
        { id: "5", title: "Conduct cyber awareness campaign", description: "Launch public awareness campaign about online scams and phishing", priority: "low" as const, icon: Megaphone }
      ];
    }
    return source.map((action, idx) => ({
      id: String(idx + 1),
      title: action,
      description: action,
      priority: (idx === 0 ? 'high' : 'medium') as 'high' | 'medium' | 'low',
      icon: [Users, MapPin, Eye, Video, Megaphone][idx % 5],
    }));
  }, [aiBriefing]);

  const mockQuickActions = [
    { id: "1", label: "Generate Intelligence Report", description: "Create a comprehensive intelligence report", icon: ClipboardList, href: '/reports' },
    { id: "2", label: "Crime Map", description: "View interactive map of crime incidents", icon: Map, href: '/hotspots' },
    { id: "3", label: "Network Analysis", description: "Analyze criminal networks", icon: Users, href: '/network-analysis' },
    { id: "4", label: "Repeat Offenders", description: "View repeat offender profiles", icon: Users, href: '/repeat-offenders' },
    { id: "5", label: "Predictive Intelligence", description: "AI-powered crime forecasting", icon: Bell, href: '/risk-scoring' },
    { id: "6", label: "Crime Search", description: "Search crimes, FIRs, suspects", icon: Search, href: '/search' },
  ];

  return (
    <div className="space-y-6">
      <OperationalStatus
        state="Karnataka"
        jurisdiction={store.jurisdiction ? store.jurisdiction.replace(/-/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()) : 'Bangalore Urban'}
        casesMonitored={summary?.total_crimes ?? 0}
        lastSync="Just now"
        aiStatus={isAiLoading ? 'Processing...' : 'Active'}
      />

      <IntelligenceScope
        onApply={handleApplyFilters}
        onReset={handleResetFilters}
      />

      {/* KPI Row */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <KpiCard label="Total Crimes" value={summary?.total_crimes ?? 0} delta={12.5} icon={<FileText size={24} />} accent="navy" />
        <KpiCard label="Active Cases" value={summary?.active_firs ?? 0} delta={-3.2} icon={<FileCheck size={24} />} accent="blue" />
        <KpiCard label="Detection Rate" value={`${detectionRate.toFixed(1)}%`} delta={5.8} icon={<ShieldAlert size={24} />} accent="green" />
        <KpiCard label="Active Hotspots" value={5} delta={10.0} icon={<MapPin size={24} />} accent="red" />
        <KpiCard label="Repeat Offenders" value={12} delta={-2.1} icon={<Users size={24} />} accent="purple" />
        <KpiCard label="High-Risk Districts" value={3} delta={7.5} icon={<BarChart2 size={24} />} accent="amber" />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left Column */}
        <div className="col-span-12 lg:col-span-8 space-y-6">
          <Card className="p-6">
            <HotspotSnapshot
              title="Hotspot Snapshot"
              heatmapPreview="/heatmap-placeholder.svg"
              topHotspots={snapshotHotspots}
            />
          </Card>

          <Card className="p-6">
            <TrendIntelligence
              title="Crime Trends"
              filters={filters}
              height={320}
            />
          </Card>
        </div>

        {/* Right Column */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
          <Card className="p-6">
            <AIExecutiveSummary
              title="AI Executive Summary"
              briefing={aiBriefing}
              isLoading={isAiLoading}
              isError={aiError}
              onRefresh={refreshAi}
            />
          </Card>

          <Card className="p-6">
            <LiveIntelligenceFeed
              title="Live Intelligence Feed"
              items={
                liveFeedItems.length
                  ? liveFeedItems
                  : [
                      { id: 'empty-feed', severity: 'low' as const, time: '--', location: 'Unknown', description: 'No live intelligence at the moment.' },
                    ]
              }
            />
          </Card>

          <Card className="p-6">
            <EmergingAlerts
              title="Emerging Alerts"
              alerts={
                emergingAlertItems.length
                  ? emergingAlertItems
                  : [
                      { id: 'empty-alert', title: 'No emerging alerts', location: 'Unknown', time: '--', severity: 'low' as const, suggestedAction: 'Continue monitoring all districts.' },
                    ]
              }
            />
          </Card>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 xl:col-span-8">
          <Card className="p-6">
            <ResourceRecommendations
              title="Resource Recommendations"
              recommendations={mockResourceRecommendations}
            />
          </Card>
        </div>
        <div className="col-span-12 xl:col-span-4">
          <Card className="p-6">
            <QuickActions
              title="Quick Actions"
              actions={mockQuickActions.map(action => ({
                ...action,
                onClick: () => action.href && navigate(action.href)
              }))}
              columns={2}
            />
          </Card>
        </div>
      </div>

      {/* Recent Data */}
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-6">
          <Card className="p-6">
            <div className="mb-4 flex items-center gap-2">
              <Activity size={20} className="text-viz-blue" />
              <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Recent Crimes</h2>
            </div>
            {crimesLoading ? (
              <LoadingSkeleton variant="table" rows={5} />
            ) : recentCrimes && recentCrimes.length > 0 ? (
              <DataTable
                columns={[
                  { key: 'title', header: 'Title', render: (r) => r.title },
                  { key: 'crime_type', header: 'Type', render: (r) => r.crime_type },
                  { key: 'status', header: 'Status', render: (r) => r.status },
                  { key: 'CREATEDTIME', header: 'Created', render: (r) => new Date(r.CREATEDTIME).toLocaleDateString() },
                ]}
                data={recentCrimes}
                rowKey={(r) => r.ROWID}
                emptyTitle="No recent crimes"
                emptyDescription="Recent crimes will appear here."
                virtualized={false}
              />
            ) : (
              <EmptyState title="No recent crimes" description="Recent crimes will appear here." />
            )}
          </Card>
        </div>

        <div className="col-span-12 lg:col-span-6">
          <Card className="p-6">
            <div className="mb-4 flex items-center gap-2">
              <FileText size={20} className="text-viz-blue" />
              <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Recent FIRs</h2>
            </div>
            {firsLoading ? (
              <LoadingSkeleton variant="table" rows={5} />
            ) : recentFirs && recentFirs.length > 0 ? (
              <DataTable
                columns={[
                  { key: 'fir_number', header: 'FIR Number', render: (r) => r.fir_number },
                  { key: 'crime_id', header: 'Crime ID', render: (r) => r.crime_id },
                  { key: 'status', header: 'Status', render: (r) => r.status },
                  { key: 'CREATEDTIME', header: 'Created', render: (r) => new Date(r.CREATEDTIME).toLocaleDateString() },
                ]}
                data={recentFirs}
                rowKey={(r) => r.ROWID}
                emptyTitle="No recent FIRs"
                emptyDescription="Recent FIRs will appear here."
                virtualized={false}
              />
            ) : (
              <EmptyState title="No recent FIRs" description="Recent FIRs will appear here." />
            )}
          </Card>
        </div>
      </div>

      {/* Floating AI Assistant */}
      <AIAssistant />
    </div>
  );
};

export default Dashboard;