import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, ChartContainer } from 'shared/components';
import { useCrimeTrends } from 'features/dashboard/hooks/useDashboard';
import { crimesApi, type Crime, type CrimeFilters } from 'shared/api';
import { useFilterStore } from 'shared/state';
import type { DashboardFilters } from 'shared/api';

type Timeframe = 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
type Comparison = 'none' | 'previous_period' | 'previous_year' | 'district' | 'category';

const TIMEFRAME_OPTIONS = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Quarterly', value: 'quarterly' },
  { label: 'Yearly', value: 'yearly' },
];

const COMPARISON_OPTIONS = [
  { label: 'None', value: 'none' },
  { label: 'Previous Period', value: 'previous_period' },
  { label: 'Previous Year', value: 'previous_year' },
  { label: 'By District', value: 'district' },
  { label: 'By Crime Category', value: 'category' },
];

const SERIES_COLORS = [
  '#3b82f6',
  '#ef4444',
  '#10b981',
  '#f59e0b',
  '#8b5cf6',
  '#ec4899',
  '#06b6d4',
  '#f97316',
];

function bucketPeriod(created: string, timeframe: Timeframe): string {
  const dt = new Date(created);
  const year = dt.getUTCFullYear();
  const month = dt.getUTCMonth();
  if (timeframe === 'daily') {
    return created.slice(0, 10);
  }
  if (timeframe === 'weekly') {
    const day = dt.getUTCDate();
    const week = Math.ceil(day / 7);
    return `${year}-W${String(Math.min(week, 5)).padStart(2, '0')}`;
  }
  if (timeframe === 'monthly') {
    return `${year}-${String(month + 1).padStart(2, '0')}`;
  }
  if (timeframe === 'quarterly') {
    return `${year}-Q${Math.floor(month / 3) + 1}`;
  }
  if (timeframe === 'yearly') {
    return `${year}`;
  }
  return created.slice(0, 10);
}

function getPreviousRange(
  dateRange: DashboardFilters['dateRange'],
  timeframe: Timeframe,
): DashboardFilters['dateRange'] {
  if (!dateRange?.start || !dateRange?.end) return undefined;
  const start = new Date(dateRange.start);
  const end = new Date(dateRange.end);
  let prevStart: Date;
  let prevEnd: Date;

  if (timeframe === 'yearly') {
    prevStart = new Date(start.getUTCFullYear() - 1, 0, 1);
    prevEnd = new Date(start.getUTCFullYear() - 1, 11, 31);
  } else if (timeframe === 'quarterly') {
    prevStart = new Date(start.getUTCFullYear(), start.getUTCMonth() - 3, 1);
    prevEnd = new Date(start.getUTCFullYear(), start.getUTCMonth() - 1, 0);
  } else if (timeframe === 'monthly') {
    prevStart = new Date(start.getUTCFullYear(), start.getUTCMonth() - 1, 1);
    prevEnd = new Date(start.getUTCFullYear(), start.getUTCMonth() - 1, 0);
  } else if (timeframe === 'weekly') {
    prevStart = new Date(start.getTime() - 7 * 24 * 60 * 60 * 1000);
    prevEnd = new Date(end.getTime() - 7 * 24 * 60 * 60 * 1000);
  } else {
    prevStart = new Date(start.getTime() - 24 * 60 * 60 * 1000);
    prevEnd = new Date(end.getTime() - 24 * 60 * 60 * 1000);
  }

  return {
    start: prevStart.toISOString().slice(0, 10),
    end: prevEnd.toISOString().slice(0, 10),
  };
}

function aggregateRawCrimes(
  crimes: Crime[],
  timeframe: Timeframe,
  groupKey: 'district_id' | 'crime_type',
): Array<Record<string, string | number>> {
  const buckets = new Map<string, Map<string, number>>();
  const groupOrder: string[] = [];

  crimes.forEach((c) => {
    const period = bucketPeriod(c.CREATEDTIME, timeframe);
    const key = (c[groupKey] as string) || 'unknown';
    if (!buckets.has(period)) buckets.set(period, new Map());
    const periodMap = buckets.get(period)!;
    if (!periodMap.has(key)) {
      groupOrder.push(key);
    }
    periodMap.set(key, (periodMap.get(key) || 0) + 1);
  });

  return Array.from(buckets.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([period, groupMap]) => {
      const row: Record<string, string | number> = { period };
      groupOrder.forEach((g) => {
        row[g] = groupMap.get(g) || 0;
      });
      return row;
    });
}

function normalizeYearPeriod(period: string, timeframe: Timeframe): string {
  if (timeframe === 'yearly') return period;
  if (timeframe === 'quarterly') {
    const parts = period.split('-');
    return parts[1] || period;
  }
  if (timeframe === 'monthly') {
    const parts = period.split('-');
    return parts[1] || period;
  }
  if (timeframe === 'weekly') {
    const parts = period.split('-');
    return parts[1] || period;
  }
  return period.slice(5);
}

const Trends: React.FC = () => {
  const store = useFilterStore();
  const [timeframe, setTimeframe] = useState<Timeframe>('monthly');
  const [comparison, setComparison] = useState<Comparison>('none');

  const effectiveFilters = useMemo<DashboardFilters>(() => {
    const base: DashboardFilters = {};
    if (store.jurisdiction) base.jurisdiction = store.jurisdiction;
    if (store.policeStation) base.policeStation = store.policeStation;
    if (store.dateRange) base.dateRange = store.dateRange;
    if (store.caseCategory && store.caseCategory.length > 0) base.caseCategory = store.caseCategory;
    if (store.severity) base.severity = store.severity;
    if (store.crimeStatus) base.crimeStatus = store.crimeStatus;
    return base;
  }, [store]);

  const { data: baseTrends } = useCrimeTrends(timeframe, effectiveFilters);

  const prevRange = useMemo(() => {
    if (comparison === 'previous_period' || comparison === 'previous_year') {
      return getPreviousRange(effectiveFilters.dateRange, timeframe);
    }
    return null;
  }, [comparison, effectiveFilters.dateRange, timeframe]);

  const prevFilters = useMemo<DashboardFilters>(() => {
    if (!prevRange) return {};
    return { ...effectiveFilters, dateRange: prevRange };
  }, [prevRange, effectiveFilters]);

  const { data: prevTrends } = useCrimeTrends(timeframe, prevFilters);

  const rawCrimeFilters = useMemo<CrimeFilters>(() => {
    const base: CrimeFilters = { limit: 10000 };
    if (effectiveFilters.jurisdiction) base.district_id = effectiveFilters.jurisdiction;
    if (effectiveFilters.policeStation) base.station_id = effectiveFilters.policeStation;
    if (effectiveFilters.dateRange?.start) base.date_from = effectiveFilters.dateRange.start;
    if (effectiveFilters.dateRange?.end) base.date_to = effectiveFilters.dateRange.end;
    if (effectiveFilters.caseCategory && effectiveFilters.caseCategory.length > 0) {
      base.crime_type = effectiveFilters.caseCategory[0];
    }
    if (effectiveFilters.severity) base.status = effectiveFilters.severity.toUpperCase();
    return base;
  }, [effectiveFilters]);

  const { data: rawCrimes } = useQuery({
    queryKey: ['crimes', 'trends-analysis', comparison, rawCrimeFilters],
    queryFn: () => crimesApi.list(rawCrimeFilters).then((res) => res.data),
    enabled: comparison === 'district' || comparison === 'category',
    staleTime: 60_000,
  });

  const chartData = useMemo(() => {
    if (comparison === 'district' || comparison === 'category') {
      if (!rawCrimes || rawCrimes.length === 0) return [];
      const groupKey = comparison === 'district' ? 'district_id' : 'crime_type';
      return aggregateRawCrimes(rawCrimes, timeframe, groupKey);
    }

    const currentMap = new Map<string, number>();
    (baseTrends || []).forEach((t) => {
      const key = comparison === 'previous_year' ? normalizeYearPeriod(t.period, timeframe) : t.period;
      currentMap.set(key, (currentMap.get(key) || 0) + t.count);
    });

    const prevMap = new Map<string, number>();
    (prevTrends || []).forEach((t) => {
      const key = comparison === 'previous_year' ? normalizeYearPeriod(t.period, timeframe) : t.period;
      prevMap.set(key, (prevMap.get(key) || 0) + t.count);
    });

    const allKeys = Array.from(new Set([...currentMap.keys(), ...prevMap.keys()])).sort();

    if (comparison === 'none') {
      return Array.from(currentMap.entries()).map(([period, value]) => ({ period, value }));
    }

    return allKeys.map((period) => ({
      period,
      'Current Period': currentMap.get(period) || 0,
      'Previous Period': prevMap.get(period) || 0,
    }));
  }, [baseTrends, prevTrends, comparison, timeframe, rawCrimes]);

  const series = useMemo(() => {
    if (comparison === 'district' || comparison === 'category') {
      if (!rawCrimes || rawCrimes.length === 0) {
        return [{ key: 'value', color: '#3b82f6', label: 'Count' }];
      }
      const groupKey = comparison === 'district' ? 'district_id' : 'crime_type';
      const groups = new Set<string>();
      rawCrimes.forEach((c) => groups.add((c[groupKey] as string) || 'unknown'));
      return Array.from(groups)
        .sort()
        .map((key, i) => ({
          key,
          color: SERIES_COLORS[i % SERIES_COLORS.length],
          label: comparison === 'district' ? `District ${key}` : key,
        }));
    }

    if (comparison === 'previous_period' || comparison === 'previous_year') {
      return [
        {
          key: 'Current Period',
          color: '#3b82f6',
          label: comparison === 'previous_year' ? 'Current Year' : 'Current Period',
        },
        {
          key: 'Previous Period',
          color: '#94a3b8',
          label: comparison === 'previous_year' ? 'Previous Year' : 'Previous Period',
        },
      ];
    }

    return [{ key: 'value', color: '#3b82f6', label: 'Crimes' }];
  }, [comparison, rawCrimes]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-700 dark:text-white">Crime Trends & Forecasting</h1>
        <p className="text-sm text-gov-slate">Historical patterns and predictive trend analysis</p>
      </div>

      <Card className="p-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-end gap-4">
            <div className="flex flex-col gap-2">
              <span className="text-sm font-medium text-gray-700">Timeframe</span>
              <div className="flex flex-wrap gap-2">
                {TIMEFRAME_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setTimeframe(option.value as Timeframe)}
                    className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                      timeframe === option.value
                        ? 'bg-navy-500 text-white'
                        : 'bg-gray-100 text-gov-slate hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <span className="text-sm font-medium text-gray-700">Comparison</span>
              <div className="flex flex-wrap gap-2">
                {COMPARISON_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setComparison(option.value as Comparison)}
                    className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors ${
                      comparison === option.value
                        ? 'bg-navy-500 text-white'
                        : 'bg-gray-100 text-gov-slate hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-4">
        {chartData.length > 0 ? (
          <ChartContainer
            title="Case Volume"
            type="bar"
            data={chartData}
            xKey="period"
            series={series}
            height={400}
          />
        ) : (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">No trend data available</div>
        )}
      </Card>

      <Card className="p-6">
        <h2 className="text-lg font-semibold text-navy-700 dark:text-white">Forecast Models</h2>
        <p className="mt-2 text-sm text-gov-slate">
          Trend forecasts are generated from district-level time series aggregated by case category and jurisdiction scope.
        </p>
      </Card>
    </div>
  );
};

export default Trends;
