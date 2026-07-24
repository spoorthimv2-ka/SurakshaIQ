import { create } from 'zustand';

export interface FilterStoreState {
  jurisdiction: string | null;
  districtId: string | null;
  policeStation: string | null;
  dateRange: { start: string; end: string } | null;
  caseCategory: string[] | null;
  severity: string | null;
  crimeStatus: string | null;
  timePreset: 'today' | 'last7' | 'last30' | 'custom' | null;
  setJurisdiction: (jurisdiction: string | null) => void;
  setDistrictId: (districtId: string | null) => void;
  setPoliceStation: (policeStation: string | null) => void;
  setDateRange: (range: { start: string; end: string } | null) => void;
  setCaseCategory: (categories: string[] | null) => void;
  setSeverity: (severity: string | null) => void;
  setCrimeStatus: (crimeStatus: string | null) => void;
  setTimePreset: (timePreset: 'today' | 'last7' | 'last30' | 'custom' | null) => void;
  resetFilters: () => void;
}

const DEFAULT_PRESET: 'today' | 'last7' | 'last30' | 'custom' = 'today';

const getDefaultDateRange = () => {
  const toISODate = (date: Date) => date.toISOString().split('T')[0];
  const today = () => toISODate(new Date());
  const daysAgo = (n: number) => toISODate(new Date(Date.now() - n * 24 * 60 * 60 * 1000));
  return { start: daysAgo(30), end: today() };
};

export const useFilterStore = create<FilterStoreState>((set) => ({
  jurisdiction: null,
  districtId: null,
  policeStation: null,
  dateRange: getDefaultDateRange(),
  caseCategory: null,
  severity: null,
  crimeStatus: null,
  timePreset: DEFAULT_PRESET,
  setJurisdiction: (jurisdiction) => set({ jurisdiction }),
  setDistrictId: (districtId) => set({ districtId }),
  setPoliceStation: (policeStation) => set({ policeStation }),
  setDateRange: (dateRange) => set({ dateRange }),
  setCaseCategory: (caseCategory) => set({ caseCategory }),
  setSeverity: (severity) => set({ severity }),
  setCrimeStatus: (crimeStatus) => set({ crimeStatus }),
  setTimePreset: (timePreset) => set({ timePreset }),
  resetFilters: () => set({
    jurisdiction: null,
    districtId: null,
    policeStation: null,
    dateRange: getDefaultDateRange(),
    caseCategory: null,
    severity: null,
    crimeStatus: null,
    timePreset: DEFAULT_PRESET,
  }),
}));
