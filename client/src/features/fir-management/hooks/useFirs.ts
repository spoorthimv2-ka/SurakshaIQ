import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { firsApi, type FirCreate, type FirUpdate, type FirFilters } from 'shared/api';

export function useFirs(filters?: FirFilters) {
  return useQuery({
    queryKey: ['firs', filters],
    queryFn: () => firsApi.list(filters).then((res) => res.data),
  });
}

export function useFir(id: string) {
  return useQuery({
    queryKey: ['firs', id],
    queryFn: () => firsApi.getById(id).then((res) => res.data),
    enabled: !!id,
  });
}

export function useCreateFir() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: FirCreate) => firsApi.create(data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['firs'] });
    },
  });
}

export function useUpdateFir() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: FirUpdate }) =>
      firsApi.update(id, data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['firs'] });
    },
  });
}

export function useDeleteFir() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => firsApi.delete(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['firs'] });
    },
  });
}
