import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertsApi, type AlertRecord, type AlertSummary, type AlertFilters } from 'shared/api';

export function useAlerts(filters?: AlertFilters) {
  return useQuery({
    queryKey: ['alerts', filters],
    queryFn: () => alertsApi.list(filters).then((res) => res.data),
  });
}

export function useAlertSummary() {
  return useQuery({
    queryKey: ['alerts', 'summary'],
    queryFn: () => alertsApi.getSummary().then((res) => res.data),
  });
}

export function useActiveAlerts(limit = 100, offset = 0, filters?: { district_id?: string; station_id?: string; severity?: string; status?: string }) {
  return useQuery({
    queryKey: ['alerts', 'active', limit, offset, filters],
    queryFn: () => alertsApi.getActive(limit, offset, filters).then((res) => res.data),
  });
}

export function useAlert(id: string) {
  return useQuery({
    queryKey: ['alerts', id],
    queryFn: () => alertsApi.getById(id).then((res) => res.data),
    enabled: !!id,
  });
}

export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => alertsApi.acknowledge(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
}

export function useResolveAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => alertsApi.resolve(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
}

export type { AlertRecord, AlertSummary, AlertFilters };
