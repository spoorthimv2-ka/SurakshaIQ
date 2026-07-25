import { apiClient } from 'services/api';

export interface UserSettings {
  user_id: string;
  theme: string;
  language: string;
  notifications_enabled: boolean;
  email_alerts: boolean;
  push_notifications: boolean;
  ai_suggestions: boolean;
  default_district_id?: string;
  default_station_id?: string;
  timezone: string;
}

export interface SystemSettings {
  key: string;
  value: any;
  description: string;
  updated_at: string;
}

export interface Notification {
  notification_id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  severity: string;
  read: boolean;
  dismissed: boolean;
  created_at: string;
  read_at?: string;
  metadata: Record<string, unknown>;
}

export interface NotificationSummary {
  total: number;
  unread: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
}

export interface ExportRequest {
  report_type: string;
  format: string;
  filters?: Record<string, any>;
  data?: Record<string, any>;
}

export interface ExportResponse {
  download_url?: string;
  content?: string;
  filename: string;
  format: string;
  size_bytes: number;
}

export interface AIReportRequest {
  report_type: string;
  scope: Record<string, any>;
  analytics?: Record<string, any>;
  format?: string;
}

export interface AIReportResponse {
  report_id: string;
  title: string;
  content: string;
  format: string;
  generated_at: string;
  confidence: number;
  is_fallback: boolean;
  sections: string[];
}

export const settingsApi = {
  getUserSettings: () =>
    apiClient.get<UserSettings>('/settings/user'),

  updateUserSettings: (data: Partial<UserSettings>) =>
    apiClient.put<UserSettings>('/settings/user', data),

  getSystemSettings: () =>
    apiClient.get<SystemSettings[]>('/settings/system'),

  getNotifications: (unreadOnly = false) =>
    apiClient.get<Notification[]>('/settings/notifications', { params: { unread_only: unreadOnly } }),

  getNotificationSummary: () =>
    apiClient.get<NotificationSummary>('/settings/notifications/summary'),

  markNotificationRead: (notificationId: string) =>
    apiClient.patch(`/settings/notifications/${notificationId}/read`, {}),

  dismissNotification: (notificationId: string) =>
    apiClient.patch(`/settings/notifications/${notificationId}/dismiss`, {}),

  clearAllNotifications: () =>
    apiClient.post('/settings/notifications/clear-all'),

  exportData: (data: ExportRequest) =>
    apiClient.post<ExportResponse>('/settings/export', data),

  generateAIReport: (data: AIReportRequest) =>
    apiClient.post<AIReportResponse>('/settings/reports/ai-generate', data),
};
