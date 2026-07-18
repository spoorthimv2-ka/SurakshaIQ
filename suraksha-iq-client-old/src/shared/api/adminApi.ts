import apiClient from './client';
import { buildCursorParams } from './pagination';
import type { CursorPaginationParams, PaginatedResponse } from './pagination';

export interface AdminUser {
  id: string;
  name: string;
  email: string;
  role: string;
  active: boolean;
}

export interface AlertRule {
  id: string;
  name: string;
  condition: string;
  enabled: boolean;
}

export const adminApi = {
  users: {
    list: (params?: CursorPaginationParams & Record<string, unknown>) =>
      apiClient.get<PaginatedResponse<AdminUser>>('/admin/users', { params: buildCursorParams(params ?? {}) }),

    create: (data: Partial<AdminUser>) => apiClient.post<AdminUser>('/admin/users', data),

    update: (id: string, data: Partial<AdminUser>) => apiClient.put<AdminUser>(`/admin/users/${id}`, data),

    delete: (id: string) => apiClient.delete<void>(`/admin/users/${id}`),
  },

  roles: {
    list: () => apiClient.get<string[]>('/admin/roles'),
  },

  alertRules: {
    list: (params?: CursorPaginationParams & Record<string, unknown>) =>
      apiClient.get<PaginatedResponse<AlertRule>>('/admin/alert-rules', {
        params: buildCursorParams(params ?? {}),
      }),

    create: (data: Partial<AlertRule>) => apiClient.post<AlertRule>('/admin/alert-rules', data),

    update: (id: string, data: Partial<AlertRule>) =>
      apiClient.put<AlertRule>(`/admin/alert-rules/${id}`, data),

    delete: (id: string) => apiClient.delete<void>(`/admin/alert-rules/${id}`),
  },
};
