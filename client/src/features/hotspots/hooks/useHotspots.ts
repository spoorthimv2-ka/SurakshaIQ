import { useQuery } from '@tanstack/react-query';
import { hotspotsApi, type Hotspot, type DistrictHotspot, type StationHotspot, type HotspotSummary, type HotspotFilters } from 'shared/api';
import { useFilterStore } from 'shared/state';

export function useHotspots(filters?: HotspotFilters) {
  return useQuery({
    queryKey: ['hotspots', filters],
    queryFn: () => hotspotsApi.list(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useDistrictHotspots(filters?: { start_date?: string; end_date?: string }) {
  return useQuery({
    queryKey: ['hotspots', 'districts', filters],
    queryFn: () => hotspotsApi.getDistrictHotspots(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useStationHotspots(filters?: { start_date?: string; end_date?: string }) {
  return useQuery({
    queryKey: ['hotspots', 'stations', filters],
    queryFn: () => hotspotsApi.getStationHotspots(filters).then((res) => res.data),
    staleTime: 60_000,
  });
}

export function useTopHotspots(limit = 10, filters?: { start_date?: string; end_date?: string }) {
  return useQuery({
    queryKey: ['hotspots', 'top', limit, filters],
    queryFn: () => hotspotsApi.getTopHotspots(limit, filters).then((res) => res.data),
    staleTime: 30_000,
  });
}

export function useGlobalHotspotFilters(): HotspotFilters {
  const store = useFilterStore();
  return {
    district_id: store.districtId ?? undefined,
    station_id: store.policeStation ?? undefined,
    crime_type: store.caseCategory?.[0],
    status: store.crimeStatus ?? undefined,
    start_date: store.dateRange?.start,
    end_date: store.dateRange?.end,
    limit: 100,
  };
}

export type { Hotspot, DistrictHotspot, StationHotspot, HotspotSummary, HotspotFilters };