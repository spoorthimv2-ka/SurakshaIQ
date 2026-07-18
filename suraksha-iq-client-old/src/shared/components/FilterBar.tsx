import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useFilterStore } from 'shared/state';

const JURISDICTIONS = [
  { value: '', label: 'All Jurisdictions' },
  { value: 'bangalore-urban', label: 'Bangalore Urban' },
  { value: 'mysuru', label: 'Mysuru' },
  { value: 'belagavi', label: 'Belagavi' },
  { value: 'mangaluru', label: 'Mangaluru' },
];

const CATEGORIES = [
  { value: 'theft', label: 'Theft' },
  { value: 'robbery', label: 'Robbery' },
  { value: 'assault', label: 'Assault' },
  { value: 'cybercrime', label: 'Cybercrime' },
  { value: 'narcotics', label: 'Narcotics' },
];

interface FilterBarProps {
  syncToUrl?: boolean;
}

const FilterBar: React.FC<FilterBarProps> = ({ syncToUrl = true }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const {
    jurisdiction,
    dateRange,
    caseCategory,
    setJurisdiction,
    setDateRange,
    setCaseCategory,
  } = useFilterStore();

  useEffect(() => {
    if (!syncToUrl) return;
    const urlJurisdiction = searchParams.get('jurisdiction');
    const urlStart = searchParams.get('startDate');
    const urlEnd = searchParams.get('endDate');
    const urlCategories = searchParams.get('category');

    if (urlJurisdiction) setJurisdiction(urlJurisdiction);
    if (urlStart && urlEnd) setDateRange({ start: urlStart, end: urlEnd });
    if (urlCategories) setCaseCategory(urlCategories.split(','));
  }, [searchParams, setCaseCategory, setDateRange, setJurisdiction, syncToUrl]);

  const updateUrl = (updates: Record<string, string | null>) => {
    if (!syncToUrl) return;
    const params = new URLSearchParams(searchParams);
    Object.entries(updates).forEach(([key, value]) => {
      if (value) params.set(key, value);
      else params.delete(key);
    });
    setSearchParams(params, { replace: true });
  };

  const handleCategoryToggle = (category: string) => {
    const current = caseCategory ?? [];
    const next = current.includes(category)
      ? current.filter((c) => c !== category)
      : [...current, category];
    setCaseCategory(next.length ? next : null);
    updateUrl({ category: next.length ? next.join(',') : null });
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="flex flex-wrap gap-4">
        <div className="min-w-[180px]">
          <label htmlFor="filter-jurisdiction" className="mb-1 block text-sm font-medium text-gov-slate">
            Jurisdiction
          </label>
          <select
            id="filter-jurisdiction"
            value={jurisdiction ?? ''}
            onChange={(e) => {
              const value = e.target.value || null;
              setJurisdiction(value);
              updateUrl({ jurisdiction: value });
            }}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
          >
            {JURISDICTIONS.map((j) => (
              <option key={j.value} value={j.value}>
                {j.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="filter-start" className="mb-1 block text-sm font-medium text-gov-slate">
            Start Date
          </label>
          <input
            id="filter-start"
            type="date"
            value={dateRange?.start ?? ''}
            onChange={(e) => {
              const start = e.target.value;
              const range = start && dateRange?.end ? { start, end: dateRange.end } : start ? { start, end: start } : null;
              setDateRange(range);
              updateUrl({ startDate: start || null, endDate: range?.end ?? null });
            }}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
          />
        </div>

        <div>
          <label htmlFor="filter-end" className="mb-1 block text-sm font-medium text-gov-slate">
            End Date
          </label>
          <input
            id="filter-end"
            type="date"
            value={dateRange?.end ?? ''}
            onChange={(e) => {
              const end = e.target.value;
              const range = dateRange?.start && end ? { start: dateRange.start, end } : null;
              setDateRange(range);
              updateUrl({ endDate: end || null, startDate: range?.start ?? null });
            }}
            className="rounded-lg border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
          />
        </div>

        <div className="flex-1 min-w-[240px]">
          <span className="mb-1 block text-sm font-medium text-gov-slate">Case Categories</span>
          <div className="flex flex-wrap gap-2">
            {CATEGORIES.map((cat) => {
              const selected = caseCategory?.includes(cat.value) ?? false;
              return (
                <button
                  key={cat.value}
                  type="button"
                  onClick={() => handleCategoryToggle(cat.value)}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                    selected
                      ? 'bg-navy-500 text-white'
                      : 'bg-gray-100 text-gov-slate hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700'
                  }`}
                >
                  {cat.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FilterBar;
