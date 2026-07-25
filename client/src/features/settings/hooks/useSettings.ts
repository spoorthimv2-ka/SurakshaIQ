import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { settingsApi, type UserSettings, type ExportRequest, type AIReportRequest } from 'shared/api';

export function useUserSettings() {
  return useQuery({
    queryKey: ['settings', 'user'],
    queryFn: async () => {
      const res = await settingsApi.getUserSettings();
      return res.data;
    },
    staleTime: 60_000,
  });
}

export function useUpdateUserSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Partial<UserSettings>) => {
      const res = await settingsApi.updateUserSettings(data);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });
}

export function useSystemSettings() {
  return useQuery({
    queryKey: ['settings', 'system'],
    queryFn: async () => {
      const res = await settingsApi.getSystemSettings();
      return res.data;
    },
    staleTime: 5 * 60_000,
  });
}

export function useNotifications(unreadOnly = false) {
  return useQuery({
    queryKey: ['settings', 'notifications', unreadOnly],
    queryFn: async () => {
      const res = await settingsApi.getNotifications(unreadOnly);
      return res.data;
    },
    staleTime: 10_000,
  });
}

export function useNotificationSummary() {
  return useQuery({
    queryKey: ['settings', 'notifications', 'summary'],
    queryFn: async () => {
      const res = await settingsApi.getNotificationSummary();
      return res.data;
    },
    staleTime: 10_000,
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (notificationId: string) => {
      const res = await settingsApi.markNotificationRead(notificationId);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'notifications'] });
    },
  });
}

export function useDismissNotification() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (notificationId: string) => {
      const res = await settingsApi.dismissNotification(notificationId);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'notifications'] });
    },
  });
}

export function useClearAllNotifications() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const res = await settingsApi.clearAllNotifications();
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings', 'notifications'] });
    },
  });
}

export function useExportData() {
  return useMutation({
    mutationFn: async (data: ExportRequest) => {
      const res = await settingsApi.exportData(data);
      return res.data;
    },
  });
}

export function useGenerateAIReport() {
  return useMutation({
    mutationFn: async (data: AIReportRequest) => {
      const res = await settingsApi.generateAIReport(data);
      return res.data;
    },
  });
}
