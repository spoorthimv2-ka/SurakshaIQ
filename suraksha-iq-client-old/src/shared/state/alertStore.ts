import { create } from 'zustand';

export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: number;
  read: boolean;
}

export interface AlertStoreState {
  alerts: Alert[];
  unreadCount: number;
  addAlert: (alert: Alert) => void;
  removeAlert: (id: string) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearAlerts: () => void;
}

export const useAlertStore = create<AlertStoreState>((set) => ({
  alerts: [],
  unreadCount: 0,
  addAlert: (alert) => set((state) => ({
    alerts: [alert, ...state.alerts],
    unreadCount: state.unreadCount + (alert.read ? 0 : 1),
  })),
  markAsRead: (id) => set((state) => {
    const alert = state.alerts.find((a) => a.id === id);
    if (alert && !alert.read) {
      return {
        alerts: state.alerts.map((a) =>
          a.id === id ? { ...a, read: true } : a
        ),
        unreadCount: state.unreadCount - 1,
      };
    }
    return state;
  }),
  removeAlert: (id) => set((state) => {
    const alert = state.alerts.find((a) => a.id === id);
    return {
      alerts: state.alerts.filter((a) => a.id !== id),
      unreadCount: state.unreadCount - (alert && !alert.read ? 1 : 0),
    };
  }),
  markAllAsRead: () => set((state) => ({
    alerts: state.alerts.map((a) => ({ ...a, read: true })),
    unreadCount: 0,
  })),
  clearAlerts: () => set({ alerts: [], unreadCount: 0 }),
}));
