import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { Button } from 'shared/components';
import { Calendar } from 'lucide-react';
import { useFilterStore } from 'shared/state';

interface IntelligenceScopeProps {
  onApply?: () => void;
  onReset?: () => void;
}

const toISODate = (date: Date) => date.toISOString().split('T')[0];
const today = () => toISODate(new Date());
const daysAgo = (n: number) => toISODate(new Date(Date.now() - n * 24 * 60 * 60 * 1000));

const PRESET_RANGES: Record<'today' | 'last7' | 'last30', { start: string; end: string }> = {
  today: { start: today(), end: today() },
  last7: { start: daysAgo(7), end: today() },
  last30: { start: daysAgo(30), end: today() },
};

const gridClass = 'col-span-12 md:col-span-6 xl:col-span-3';
const gridClassActions = 'col-span-12 md:col-span-6 xl:col-span-3';

const IntelligenceScope: React.FC<IntelligenceScopeProps> = ({ onApply, onReset }) => {
  const store = useFilterStore();
  const [localCategories, setLocalCategories] = useState<string[]>(store.caseCategory ?? []);

  const policeStations = useMemo(() => [
    { value: 'STN-001', label: 'Bangalore Urban North', districtId: 'bangalore-urban' },
    { value: 'STN-002', label: 'Bangalore Urban South', districtId: 'bangalore-urban' },
    { value: 'STN-003', label: 'Bangalore Urban East', districtId: 'bangalore-urban' },
    { value: 'STN-004', label: 'Bangalore Urban West', districtId: 'bangalore-urban' },
    { value: 'STN-009', label: 'Mysuru North', districtId: 'mysuru' },
    { value: 'STN-010', label: 'Mysuru South', districtId: 'mysuru' },
    { value: 'STN-011', label: 'Mysuru East', districtId: 'mysuru' },
    { value: 'STN-012', label: 'Mysuru West', districtId: 'mysuru' },
    { value: 'STN-013', label: 'Belagavi North', districtId: 'belagavi' },
    { value: 'STN-014', label: 'Belagavi South', districtId: 'belagavi' },
    { value: 'STN-015', label: 'Belagavi East', districtId: 'belagavi' },
    { value: 'STN-016', label: 'Belagavi West', districtId: 'belagavi' },
    { value: 'STN-017', label: 'Mangaluru North', districtId: 'mangaluru' },
    { value: 'STN-018', label: 'Mangaluru South', districtId: 'mangaluru' },
    { value: 'STN-019', label: 'Mangaluru East', districtId: 'mangaluru' },
    { value: 'STN-020', label: 'Mangaluru West', districtId: 'mangaluru' },
  ], []);

  const jurisdictions = useMemo(() => [
    { value: '', label: 'All Jurisdictions' },
    { value: 'bangalore-urban', label: 'Bangalore Urban' },
    { value: 'mysuru', label: 'Mysuru' },
    { value: 'belagavi', label: 'Belagavi' },
    { value: 'mangaluru', label: 'Mangaluru' },
  ], []);

  const categories = useMemo(() => [
    { value: 'theft', label: 'Theft' },
    { value: 'robbery', label: 'Robbery' },
    { value: 'assault', label: 'Assault' },
    { value: 'cybercrime', label: 'Cybercrime' },
    { value: 'narcotics', label: 'Narcotics' },
    { value: 'murder', label: 'Murder' },
    { value: 'rape', label: 'Rape' },
    { value: 'kidnapping', label: 'Kidnapping' },
  ], []);

  const severities = useMemo(() => [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' },
  ], []);

  const statuses = useMemo(() => [
    { value: 'open', label: 'Open' },
    { value: 'under-investigation', label: 'Under Investigation' },
    { value: 'closed', label: 'Closed' },
    { value: 'unsolved', label: 'Unsolved' },
  ], []);

  const filteredStations = useMemo(() => {
    if (!store.jurisdiction) return [];
    return policeStations.filter((s) => s.districtId === store.jurisdiction);
  }, [store.jurisdiction, policeStations]);

  useEffect(() => {
    setLocalCategories(store.caseCategory ?? []);
  }, [store.caseCategory]);

  const handlePresetChange = useCallback((preset: 'today' | 'last7' | 'last30' | 'custom') => {
    store.setTimePreset(preset);
    if (preset !== 'custom') {
      store.setDateRange(PRESET_RANGES[preset]);
    }
  }, [store]);

  const handleApply = useCallback(() => {
    store.setCaseCategory(localCategories.length ? localCategories : null);
    onApply?.();
  }, [store, localCategories, onApply]);

  const handleReset = useCallback(() => {
    store.resetFilters();
    setLocalCategories([]);
    onReset?.();
  }, [store, onReset]);

  const handleJurisdictionChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    store.setJurisdiction(e.target.value || null);
    store.setPoliceStation(null);
  }, [store]);

  const handlePoliceStationChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    store.setPoliceStation(e.target.value || null);
  }, [store]);

  const handleDateStartChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const start = e.target.value;
    store.setDateRange(start ? { start, end: store.dateRange?.end ?? start } : null);
  }, [store]);

  const handleDateEndChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const end = e.target.value;
    store.setDateRange(end ? { start: store.dateRange?.start ?? end, end } : null);
  }, [store]);

  const handleSeverityChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    store.setSeverity(e.target.value || null);
  }, [store]);

  const handleCrimeStatusChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    store.setCrimeStatus(e.target.value || null);
  }, [store]);

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-900">
        <div className="grid grid-cols-12 gap-x-6 gap-y-5">
          {/* Row 1: 4 equal columns */}
          {/* Jurisdiction */}
          <div className={gridClass}>
            <label htmlFor="jurisdiction" className="mb-1.5 block text-sm font-medium text-gov-slate">
              Jurisdiction
            </label>
            <select
              id="jurisdiction"
              value={store.jurisdiction ?? ''}
              onChange={handleJurisdictionChange}
              className="h-10 w-full rounded-lg border border-gray-300 px-3 text-sm transition-colors hover:border-gray-400 focus:border-viz-blue focus:outline-none focus:ring-2 focus:ring-viz-blue/20 dark:border-gray-600 dark:bg-gray-800"
            >
              {jurisdictions.map((j) => (
                <option key={j.value} value={j.value}>
                  {j.label}
                </option>
              ))}
            </select>
          </div>

          {/* Police Station */}
          <div className={gridClass}>
            <label htmlFor="policeStation" className="mb-1.5 block text-sm font-medium text-gov-slate">
              Police Station
            </label>
            <select
              id="policeStation"
              value={store.policeStation ?? ''}
              onChange={handlePoliceStationChange}
              disabled={!store.jurisdiction}
              className="h-10 w-full rounded-lg border border-gray-300 px-3 text-sm transition-colors hover:border-gray-400 focus:border-viz-blue focus:outline-none focus:ring-2 focus:ring-viz-blue/20 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800"
            >
              <option value="">Select Jurisdiction First</option>
              {filteredStations.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>

          {/* Date Range */}
          <div className={gridClass}>
            <label htmlFor="dateRange" className="mb-1.5 block text-sm font-medium text-gov-slate">
              Date Range
            </label>
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Calendar className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  type="date"
                  id="dateRangeStart"
                  value={store.dateRange?.start ?? ''}
                  onChange={handleDateStartChange}
                  className="h-10 w-full rounded-lg border border-gray-300 pl-9 pr-3 text-sm transition-colors hover:border-gray-400 focus:border-viz-blue focus:outline-none focus:ring-2 focus:ring-viz-blue/20 dark:border-gray-600 dark:bg-gray-800"
                />
              </div>
              <span className="text-sm font-medium text-gray-400">to</span>
              <div className="relative flex-1">
                <Calendar className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <input
                  type="date"
                  id="dateRangeEnd"
                  value={store.dateRange?.end ?? ''}
                  onChange={handleDateEndChange}
                  className="h-10 w-full rounded-lg border border-gray-300 pl-9 pr-3 text-sm transition-colors hover:border-gray-400 focus:border-viz-blue focus:outline-none focus:ring-2 focus:ring-viz-blue/20 dark:border-gray-600 dark:bg-gray-800"
                />
              </div>
            </div>
          </div>

          {/* Crime Categories */}
          <div className={gridClass}>
            <label htmlFor="crimeCategories" className="mb-1.5 block text-sm font-medium text-gov-slate">
              Crime Categories
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {categories.map((cat) => {
                const selected = localCategories.includes(cat.value);
                return (
                  <button
                    key={cat.value}
                    type="button"
                    onClick={() => {
                      setLocalCategories((prev) =>
                        prev.includes(cat.value)
                          ? prev.filter((c) => c !== cat.value)
                          : [...prev, cat.value]
                      );
                    }}
                    className={`h-9 rounded-lg border px-2 text-xs font-medium transition-all ${
                      selected
                        ? 'border-navy-500 bg-navy-500 text-white shadow-sm'
                        : 'border-gray-300 bg-white text-gov-slate hover:border-gray-400 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:hover:bg-gray-700'
                    }`}
                  >
                    {cat.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Row 2: 4 equal columns */}
          {/* Severity */}
          <div className={gridClass}>
            <label htmlFor="severity" className="mb-1.5 block text-sm font-medium text-gov-slate">
              Severity
            </label>
            <select
              id="severity"
              value={store.severity ?? ''}
              onChange={handleSeverityChange}
              className="h-10 w-full rounded-lg border border-gray-300 px-3 text-sm transition-colors hover:border-gray-400 focus:border-viz-blue focus:outline-none focus:ring-2 focus:ring-viz-blue/20 dark:border-gray-600 dark:bg-gray-800"
            >
              <option value="">All Severities</option>
              {severities.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>

          {/* Crime Status */}
          <div className={gridClass}>
            <label htmlFor="crimeStatus" className="mb-1.5 block text-sm font-medium text-gov-slate">
              Crime Status
            </label>
            <select
              id="crimeStatus"
              value={store.crimeStatus ?? ''}
              onChange={handleCrimeStatusChange}
              className="h-10 w-full rounded-lg border border-gray-300 px-3 text-sm transition-colors hover:border-gray-400 focus:border-viz-blue focus:outline-none focus:ring-2 focus:ring-viz-blue/20 dark:border-gray-600 dark:bg-gray-800"
            >
              <option value="">All Statuses</option>
              {statuses.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>

          {/* Time Presets */}
          <div className={gridClass}>
            <label className="mb-1.5 block text-sm font-medium text-gov-slate">
              Time Preset
            </label>
            <div className="grid grid-cols-4 gap-2">
              {(['today', 'last7', 'last30', 'custom'] as const).map((preset) => (
                <button
                  key={preset}
                  type="button"
                  onClick={() => handlePresetChange(preset)}
                  className={`h-10 rounded-lg border text-xs font-medium transition-all ${
                    store.timePreset === preset
                      ? 'border-navy-500 bg-navy-500 text-white shadow-sm'
                      : 'border-gray-300 bg-white text-gov-slate hover:border-gray-400 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:hover:bg-gray-700'
                  }`}
                >
                  {preset === 'last7' ? 'Last 7 Days' : preset === 'last30' ? 'Last 30 Days' : preset.charAt(0).toUpperCase() + preset.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className={gridClassActions}>
            <label className="mb-1.5 block text-sm font-medium text-gov-slate">
              Actions
            </label>
            <div className="flex items-end gap-3">
              <Button variant="secondary" onClick={handleReset} className="flex-1">
                Reset
              </Button>
              <Button variant="primary" onClick={handleApply} className="flex-1">
                Analyze Intelligence
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntelligenceScope;