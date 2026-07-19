import { apiClient } from 'services/api';

export interface AdminUser {
  user_id: string;
  officer_id?: string;
  name: string;
  email: string;
  role: string;
  district?: string;
  station?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface AdminUserCreate {
  name: string;
  email: string;
  role: string;
  district?: string;
  station?: string;
  status?: string;
}

export interface AdminUserUpdate {
  name?: string;
  email?: string;
  role?: string;
  district?: string;
  station?: string;
  status?: string;
}

export interface RoleInfo {
  id: string;
  label: string;
  description: string;
}

export interface AdminStatistics {
  total_users: number;
  active_users: number;
  inactive_users: number;
  users_by_role: Array<{ role: string; count: number }>;
  users_by_district: Array<{ district_id: string; district_name: string; count: number }>;
}

export interface AuditLog {
  log_id: string;
  action: string;
  user: string;
  target: string;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface UserFilters {
  role?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export const adminApi = {
  users: {
    list: (filters?: UserFilters) =>
      apiClient.get<AdminUser[]>('/admin/users', { params: filters }),

    get: (id: string) =>
      apiClient.get<AdminUser>(`/admin/users/${id}`),

    create: (data: AdminUserCreate) =>
      apiClient.post<AdminUser>('/admin/users', data),

    update: (id: string, data: AdminUserUpdate) =>
      apiClient.put<AdminUser>(`/admin/users/${id}`, data),

    delete: (id: string) =>
      apiClient.delete(`/admin/users/${id}`),

    activate: (id: string) =>
      apiClient.patch<AdminUser>(`/admin/users/${id}/activate`, {}),

    deactivate: (id: string) =>
      apiClient.patch<AdminUser>(`/admin/users/${id}/deactivate`, {}),
  },

  roles: {
    list: () =>
      apiClient.get<RoleInfo[]>('/admin/roles'),
  },

  statistics: {
    get: () =>
      apiClient.get<AdminStatistics>('/admin/statistics'),
  },

  auditLogs: {
    list: (params?: { limit?: number; offset?: number }) =>
      apiClient.get<AuditLog[]>('/admin/audit-logs', { params }),
  },
};
