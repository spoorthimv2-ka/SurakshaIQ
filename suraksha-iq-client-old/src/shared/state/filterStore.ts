import { create } from 'zustand';

export interface FilterStoreState {
  jurisdiction: string | null;
  districtId: string | null;
  dateRange: { start: string; end: string } | null;
  caseCategory: string[] | null;
  setJurisdiction: (jurisdiction: string | null) => void;
  setDistrictId: (districtId: string | null) => void;
  setDateRange: (range: { start: string; end: string } | null) => void;
  setCaseCategory: (categories: string[] | null) => void;
  resetFilters: () => void;
}

export const useFilterStore = create<FilterStoreState>((set) => ({
  jurisdiction: null,
  districtId: null,
  dateRange: null,
  caseCategory: null,
  setJurisdiction: (jurisdiction) => set({ jurisdiction }),
  setDistrictId: (districtId) => set({ districtId }),
  setDateRange: (dateRange) => set({ dateRange }),
  setCaseCategory: (caseCategory) => set({ caseCategory }),
  resetFilters: () => set({
    jurisdiction: null,
    districtId: null,
    dateRange: null,
    caseCategory: null,
  }),
}));
