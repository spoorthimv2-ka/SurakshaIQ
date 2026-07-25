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

export interface AuditLogFilters {
  action?: string;
  user?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}

export interface AdminOfficer {
  officer_id: string;
  name: string;
  email: string;
  rank?: string;
  designation?: string;
  role: string;
  district?: string;
  station?: string;
  status: string;
  created_at?: string;
  updated_at?: string;
  performance_summary?: Record<string, any>;
}

export interface AdminDistrict {
  district_id: string;
  district_name: string;
  officer_count: number;
  police_station_count: number;
  statistics?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface AdminPoliceStation {
  station_id: string;
  station_name: string;
  district_id: string;
  district_name: string;
  officer_count: number;
  status: string;
  created_at?: string;
  updated_at?: string;
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

  officers: {
    list: (filters?: { limit?: number; offset?: number; station_id?: string; district_id?: string }) =>
      apiClient.get<AdminOfficer[]>('/admin/officers', { params: filters }),
  },

  districts: {
    list: (filters?: { limit?: number; offset?: number }) =>
      apiClient.get<AdminDistrict[]>('/admin/districts', { params: filters }),
  },

  policeStations: {
    list: (filters?: { limit?: number; offset?: number; district_id?: string }) =>
      apiClient.get<AdminPoliceStation[]>('/admin/police-stations', { params: filters }),
  },

  statistics: {
    get: () =>
      apiClient.get<AdminStatistics>('/admin/statistics'),
  },

  auditLogs: {
    list: (filters?: AuditLogFilters) =>
      apiClient.get<AuditLog[]>('/admin/audit-logs', { params: filters }),
  },
};
