import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminApi, type AdminUser, type AdminUserCreate, type AdminUserUpdate, type RoleInfo, type AdminStatistics, type AuditLog, type UserFilters } from 'shared/api';

export function useUsers(filters?: UserFilters) {
  return useQuery({
    queryKey: ['admin', 'users', filters],
    queryFn: () => adminApi.users.list(filters).then((res) => res.data),
    staleTime: 30_000,
  });
}

export function useUser(userId: string) {
  return useQuery({
    queryKey: ['admin', 'users', userId],
    queryFn: () => adminApi.users.get(userId).then((res) => res.data),
    enabled: !!userId,
    staleTime: 30_000,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AdminUserCreate) => adminApi.users.create(data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'statistics'] });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AdminUserUpdate }) =>
      adminApi.users.update(id, data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'statistics'] });
    },
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => adminApi.users.delete(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'statistics'] });
    },
  });
}

export function useActivateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => adminApi.users.activate(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'statistics'] });
    },
  });
}

export function useDeactivateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => adminApi.users.deactivate(id).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] });
      queryClient.invalidateQueries({ queryKey: ['admin', 'statistics'] });
    },
  });
}

export function useRoles() {
  return useQuery({
    queryKey: ['admin', 'roles'],
    queryFn: () => adminApi.roles.list().then((res) => res.data),
    staleTime: 300_000,
  });
}

export function useAdminStatistics() {
  return useQuery({
    queryKey: ['admin', 'statistics'],
    queryFn: () => adminApi.statistics.get().then((res) => res.data),
    staleTime: 30_000,
  });
}

export function useAuditLogs(filters?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ['admin', 'audit-logs', filters],
    queryFn: () => adminApi.auditLogs.list(filters).then((res) => res.data),
    staleTime: 30_000,
  });
}

export type { AdminUser, AdminUserCreate, AdminUserUpdate, RoleInfo, AdminStatistics, AuditLog, UserFilters };
