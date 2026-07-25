import React, { useMemo, useState } from 'react';
import { Card, KpiCard, ChartContainer, DataTable, LoadingSkeleton, EmptyState, AlertBanner, Badge } from 'shared/components';
import type { DataTableColumn } from 'shared/components';
import { useFilterStore } from 'shared/state';
import {
  useCrimeForecast,
  useEmergingHotspots,
  useDynamicRiskIndex,
  usePatrolRecommendations,
  useTemporalIntelligence,
  useTrendAnalysis,
  useScenarioSimulation,
  usePredictiveDashboard,
  usePredictiveAiIntelligence,
} from 'features/predictive-intelligence/hooks/usePredictiveIntelligence';
import type {
  EmergingHotspot,
  RiskIndex,
  PatrolRecommendation,
  TrendCategory,
  ScenarioSimulation,
} from 'shared/api';
import { Shield, TrendingUp, TrendingDown, Activity, MapPin, Clock, Target, Brain, Play } from 'lucide-react';

const RISK_VARIANT: Record<string, 'success' | 'warning' | 'danger' | 'secondary'> = {
  Critical: 'danger',
  High: 'warning',
  Medium: 'secondary',
  Low: 'success',
};

const TREND_VARIANT: Record<string, 'success' | 'warning' | 'danger' | 'secondary'> = {
  increasing: 'danger',
  decreasing: 'success',
  stable: 'secondary',
};

const PredictiveIntelligence: React.FC = () => {
  const { districtId, policeStation, caseCategory, timePreset, setTimePreset } = useFilterStore();
  const [scenarioDistrict, setScenarioDistrict] = useState('');
  const [scenarioStation, setScenarioStation] = useState('');
  const [scenarioCategory, setScenarioCategory] = useState('');
  const [scenarioWindow, setScenarioWindow] = useState('30d');
  const [scenarioResult, setScenarioResult] = useState<ScenarioSimulation | null>(null);

  const forecastQuery = useCrimeForecast({
    district_id: districtId || undefined,
    station_id: policeStation || undefined,
    crime_category: caseCategory?.[0] || undefined,
    time_period: timePreset === 'today' ? '7d' : timePreset === 'last7' ? '7d' : timePreset === 'last30' ? '30d' : 'quarter',
  });
  const hotspotsQuery = useEmergingHotspots({
    district_id: districtId || undefined,
  });
  const riskQuery = useDynamicRiskIndex({
    district_id: districtId || undefined,
    station_id: policeStation || undefined,
    crime_category: caseCategory?.[0] || undefined,
  });
  const patrolsQuery = usePatrolRecommendations({
    district_id: districtId || undefined,
  });
  const temporalQuery = useTemporalIntelligence({
    district_id: districtId || undefined,
    station_id: policeStation || undefined,
    crime_category: caseCategory?.[0] || undefined,
  });
  const trendsQuery = useTrendAnalysis({
    district_id: districtId || undefined,
    station_id: policeStation || undefined,
    crime_category: caseCategory?.[0] || undefined,
  });
  const dashboardQuery = usePredictiveDashboard({
    district_id: districtId || undefined,
    station_id: policeStation || undefined,
    crime_category: caseCategory?.[0] || undefined,
    time_period: timePreset === 'today' ? '7d' : timePreset === 'last7' ? '7d' : timePreset === 'last30' ? '30d' : 'quarter',
  });
  const aiQuery = usePredictiveAiIntelligence({
    district_id: districtId || undefined,
    station_id: policeStation || undefined,
    crime_category: caseCategory?.[0] || undefined,
    time_period: timePreset === 'today' ? '7d' : timePreset === 'last7' ? '7d' : timePreset === 'last30' ? '30d' : 'quarter',
  });

  const scenarioMutation = useScenarioSimulation();

  const forecastChartData = useMemo(() => {
    const forecasts = forecastQuery.data ?? [];
    if (!forecasts.length) return [];
    const first = forecasts[0];
    return first.forecast_points.map((p) => ({
      date: p.date,
      predicted: p.predicted_count,
      low: p.confidence_low,
      high: p.confidence_high,
    }));
  }, [forecastQuery.data]);

  const dashboard = dashboardQuery.data;

  const riskColumns: DataTableColumn<RiskIndex>[] = [
    { key: 'entity_name', header: 'Entity', render: (r) => r.entity_name },
    { key: 'entity_type', header: 'Type', render: (r) => r.entity_type },
    {
      key: 'risk_level',
      header: 'Level',
      render: (r) => <Badge variant={RISK_VARIANT[r.risk_level] ?? 'secondary'}>{r.risk_level}</Badge>,
    },
    {
      key: 'risk_score',
      header: 'Score',
      sortable: true,
      sortValue: (r) => r.risk_score,
      render: (r) => r.risk_score.toFixed(1),
    },
    {
      key: 'trend',
      header: 'Trend',
      render: (r) => <Badge variant={TREND_VARIANT[r.trend] ?? 'secondary'}>{r.trend}</Badge>,
    },
    {
      key: 'score_change',
      header: 'Change',
      render: (r) => (r.score_change >= 0 ? '+' : '') + r.score_change.toFixed(2),
    },
    {
      key: 'explanation',
      header: 'Explanation',
      render: (r) => <span className="text-xs text-gray-600 dark:text-gray-400 truncate block max-w-[200px]" title={r.explanation}>{r.explanation}</span>,
    },
  ];

  const hotspotColumns: DataTableColumn<EmergingHotspot>[] = [
    { key: 'district_name', header: 'District', render: (r) => r.district_name },
    { key: 'station_name', header: 'Station', render: (r) => r.station_name },
    {
      key: 'risk_level',
      header: 'Risk',
      render: (r) => <Badge variant={RISK_VARIANT[r.risk_level] ?? 'secondary'}>{r.risk_level}</Badge>,
    },
    {
      key: 'intensity',
      header: 'Intensity',
      sortable: true,
      sortValue: (r) => r.intensity,
      render: (r) => `${(r.intensity * 100).toFixed(1)}%`,
    },
    {
      key: 'confidence',
      header: 'Confidence',
      sortable: true,
      sortValue: (r) => r.confidence,
      render: (r) => `${(r.confidence * 100).toFixed(1)}%`,
    },
    { key: 'explanation', header: 'Why', render: (r) => <span className="text-xs text-gray-600 dark:text-gray-400 truncate block max-w-[200px]" title={r.explanation}>{r.explanation}</span> },
  ];

  const patrolColumns: DataTableColumn<PatrolRecommendation>[] = [
    { key: 'zone_name', header: 'Zone', render: (r) => r.zone_name },
    { key: 'zone_type', header: 'Type', render: (r) => r.zone_type },
    { key: 'recommendation_type', header: 'Action', render: (r) => r.recommendation_type },
    {
      key: 'priority',
      header: 'Priority',
      render: (r) => <Badge variant={RISK_VARIANT[r.priority] ?? 'secondary'}>{r.priority}</Badge>,
    },
    { key: 'description', header: 'Description', render: (r) => <span className="text-xs">{r.description}</span> },
    { key: 'reason', header: 'Reason', render: (r) => <span className="text-xs text-gray-600 dark:text-gray-400 truncate block max-w-[200px]" title={r.reason}>{r.reason}</span> },
  ];

  const trendColumns: DataTableColumn<TrendCategory>[] = [
    { key: 'category', header: 'Category', render: (r) => r.category },
    {
      key: 'trend',
      header: 'Trend',
      render: (r) => (
        <span className="flex items-center gap-1">
          {r.trend === 'increasing' ? <TrendingUp size={14} className="text-red-500" /> : r.trend === 'decreasing' ? <TrendingDown size={14} className="text-green-500" /> : <Activity size={14} className="text-gray-400" />}
          {r.trend}
        </span>
      ),
    },
    {
      key: 'change_percent',
      header: 'Change',
      sortable: true,
      sortValue: (r) => r.change_percent,
      render: (r) => `${r.change_percent >= 0 ? '+' : ''}${r.change_percent.toFixed(1)}%`,
    },
    { key: 'count_current', header: 'Current', render: (r) => r.count_current },
    { key: 'count_previous', header: 'Previous', render: (r) => r.count_previous },
  ];

  const ai = aiQuery.data;

  const handleScenarioSimulate = async () => {
    const result = await scenarioMutation.mutateAsync({
      district_id: scenarioDistrict || undefined,
      station_id: scenarioStation || undefined,
      crime_category: scenarioCategory || undefined,
      time_window: scenarioWindow,
    });
    setScenarioResult(result);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Predictive Intelligence</h1>
        <div className="flex items-center gap-2">
          <select
            value={timePreset || 'last30'}
            onChange={(e) => setTimePreset(e.target.value as any)}
            className="rounded border border-gray-300 bg-white px-3 py-1.5 text-sm dark:border-gray-700 dark:bg-gray-800"
          >
            <option value="today">Today</option>
            <option value="last7">Last 7 Days</option>
            <option value="last30">Last 30 Days</option>
            <option value="custom">Custom</option>
          </select>
        </div>
      </div>

      {(forecastQuery.error || hotspotsQuery.error || riskQuery.error) && (
        <AlertBanner title="Load Error" message="Some predictive data failed to load. Please try again." variant="error" />
      )}

      {/* Predictive Dashboard KPI Cards */}
      {dashboard && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <KpiCard label="Highest Risk District" value={dashboard.highest_risk_district?.entity_name || 'N/A'} icon={<Shield size={20} />} />
          <KpiCard
            label="Fastest Growing Crime"
            value={dashboard.fastest_growing_crime?.category || 'N/A'}
            delta={dashboard.fastest_growing_crime?.change_percent}
            icon={<TrendingUp size={20} />}
          />
          <KpiCard label="Emerging Hotspot" value={dashboard.emerging_hotspot?.district_name || 'N/A'} icon={<MapPin size={20} />} />
          <KpiCard label="Forecast Confidence" value={`${(dashboard.forecast_confidence * 100).toFixed(0)}%`} icon={<Activity size={20} />} />
          <KpiCard label="Patrol Increase" value={`+${dashboard.recommended_patrol_increase}`} delta={dashboard.recommended_patrol_increase} icon={<Target size={20} />} />
          <KpiCard label="Predicted Incidents" value={dashboard.predicted_incident_count.toLocaleString()} icon={<Clock size={20} />} />
        </div>
      )}

      {/* Crime Forecasting */}
      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Crime Forecast</h2>
        {forecastQuery.isLoading ? (
          <LoadingSkeleton variant="table" />
        ) : forecastQuery.error ? (
          <EmptyState title="Failed to load forecast" />
        ) : (
          <ChartContainer
            title="Predicted Crime Count"
            type="line"
            data={forecastChartData}
            xKey="date"
            series={[
              { key: 'predicted', color: '#3b82f6', label: 'Predicted' },
              { key: 'low', color: '#93c5fd', label: 'Low (90% CI)' },
              { key: 'high', color: '#93c5fd', label: 'High (90% CI)' },
            ]}
            height={320}
          />
        )}
      </Card>

      {/* Emerging Hotspots + Dynamic Risk Index */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Emerging Hotspots</h2>
          {hotspotsQuery.isLoading ? (
            <LoadingSkeleton variant="table" />
          ) : hotspotsQuery.error ? (
            <EmptyState title="Failed to load hotspots" />
          ) : (
            <DataTable columns={hotspotColumns} data={hotspotsQuery.data ?? []} rowKey={(r) => r.id} pageSize={10} />
          )}
        </Card>
        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Dynamic Risk Index</h2>
          {riskQuery.isLoading ? (
            <LoadingSkeleton variant="table" />
          ) : riskQuery.error ? (
            <EmptyState title="Failed to load risk index" />
          ) : (
            <DataTable columns={riskColumns} data={riskQuery.data ?? []} rowKey={(r) => r.entity_id} pageSize={10} />
          )}
        </Card>
      </div>

      {/* Patrol Deployment Intelligence */}
      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Patrol Deployment Intelligence</h2>
        {patrolsQuery.isLoading ? (
          <LoadingSkeleton variant="table" />
        ) : patrolsQuery.error ? (
          <EmptyState title="Failed to load patrol recommendations" />
        ) : (
          <DataTable columns={patrolColumns} data={patrolsQuery.data ?? []} rowKey={(r) => r.zone_id} pageSize={10} />
        )}
      </Card>

      {/* Temporal Intelligence + Trend Analysis */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Temporal Intelligence</h2>
          {temporalQuery.isLoading ? (
            <LoadingSkeleton variant="table" />
          ) : temporalQuery.data ? (
            <div className="space-y-4">
              <ChartContainer
                title="Hourly Distribution"
                type="bar"
                data={(temporalQuery.data.hourly_distribution ?? []).map((d) => ({ hour: d.hour ?? 0, count: d.count }))}
                xKey="hour"
                series={[{ key: 'count', color: '#3b82f6', label: 'Incidents' }]}
                height={200}
              />
              <ChartContainer
                title="Monthly Distribution"
                type="bar"
                data={(temporalQuery.data.monthly_distribution ?? []).map((d) => ({ month: d.month ?? '', count: d.count }))}
                xKey="month"
                series={[{ key: 'count', color: '#10b981', label: 'Incidents' }]}
                height={200}
              />
            </div>
          ) : (
            <EmptyState title="No temporal data" />
          )}
        </Card>
        <Card className="p-6">
          <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Trend Analysis</h2>
          {trendsQuery.isLoading ? (
            <LoadingSkeleton variant="table" />
          ) : trendsQuery.data ? (
            <div className="space-y-4">
              <DataTable columns={trendColumns} data={trendsQuery.data.increasing_categories} rowKey={(r) => r.category} pageSize={5} />
              <p className="text-sm text-gray-600 dark:text-gray-400">Overall trend: <Badge variant={trendsQuery.data.overall_trend === 'increasing' ? 'danger' : trendsQuery.data.overall_trend === 'decreasing' ? 'success' : 'secondary'}>{trendsQuery.data.overall_trend}</Badge></p>
            </div>
          ) : (
            <EmptyState title="No trend data" />
          )}
        </Card>
      </div>

      {/* Scenario Simulator */}
      <Card className="p-6">
        <h2 className="mb-4 text-lg font-semibold text-navy-700 dark:text-white">Scenario Simulator</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <input
            type="text"
            placeholder="District ID"
            value={scenarioDistrict}
            onChange={(e) => setScenarioDistrict(e.target.value)}
            className="rounded border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-800"
          />
          <input
            type="text"
            placeholder="Station ID"
            value={scenarioStation}
            onChange={(e) => setScenarioStation(e.target.value)}
            className="rounded border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-800"
          />
          <input
            type="text"
            placeholder="Crime Category"
            value={scenarioCategory}
            onChange={(e) => setScenarioCategory(e.target.value)}
            className="rounded border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-800"
          />
          <select
            value={scenarioWindow}
            onChange={(e) => setScenarioWindow(e.target.value)}
            className="rounded border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-800"
          >
            <option value="7d">Next 7 Days</option>
            <option value="30d">Next 30 Days</option>
            <option value="quarter">Next Quarter</option>
          </select>
        </div>
        <div className="mt-4">
          <button
            onClick={handleScenarioSimulate}
            disabled={scenarioMutation.isPending}
            className="flex items-center gap-2 rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            <Play size={16} />
            {scenarioMutation.isPending ? 'Simulating...' : 'Run Simulation'}
          </button>
        </div>
        {scenarioMutation.error && (
          <AlertBanner title="Simulation Failed" message="Scenario simulation failed." variant="error" className="mt-4" />
        )}
        {scenarioResult && (
          <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Card className="p-4">
              <h3 className="font-semibold text-navy-700 dark:text-white">Forecast</h3>
              <pre className="mt-2 overflow-auto text-xs text-gray-800 dark:text-gray-200">{JSON.stringify(scenarioResult.forecast, null, 2)}</pre>
            </Card>
            <Card className="p-4">
              <h3 className="font-semibold text-navy-700 dark:text-white">Risk</h3>
              <pre className="mt-2 overflow-auto text-xs text-gray-800 dark:text-gray-200">{JSON.stringify(scenarioResult.risk, null, 2)}</pre>
            </Card>
          </div>
        )}
      </Card>

      {/* AI Intelligence */}
      <Card className="p-6">
        <div className="mb-4 flex items-center gap-2">
          <Brain size={20} className="text-purple-600" />
          <h2 className="text-lg font-semibold text-navy-700 dark:text-white">AI Intelligence</h2>
        </div>
        {aiQuery.isLoading ? (
          <LoadingSkeleton variant="table" />
        ) : aiQuery.data ? (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Forecast Explanation</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">{ai!.forecast_explanation}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Risk Explanation</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">{ai!.risk_explanation}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Strategy Recommendations</p>
              <ul className="list-disc space-y-1 pl-5 text-sm text-gray-600 dark:text-gray-400">
                {ai!.strategy_recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Executive Summary</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">{ai!.executive_summary}</p>
              <p className="mt-1 text-xs text-gray-500">Confidence: {(ai!.confidence * 100).toFixed(0)}% {ai!.is_fallback ? '(deterministic fallback)' : '(AI)'}</p>
            </div>
          </div>
        ) : (
          <EmptyState title="No AI intelligence available" />
        )}
      </Card>
    </div>
  );
};

export default PredictiveIntelligence;
