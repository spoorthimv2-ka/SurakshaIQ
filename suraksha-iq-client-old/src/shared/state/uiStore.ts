import { create } from 'zustand';

export interface UIStoreState {
  sidebarCollapsed: boolean;
  activeTheme: 'light' | 'dark';
  activeModal: string | null;
  activeDrawer: string | null;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setActiveTheme: (theme: 'light' | 'dark') => void;
  openModal: (id: string) => void;
  closeModal: () => void;
  openDrawer: (id: string) => void;
  closeDrawer: () => void;
}

export const useUIStore = create<UIStoreState>((set) => ({
  sidebarCollapsed: false,
  activeTheme:
    (typeof localStorage !== 'undefined'
      ? (localStorage.getItem('theme') as 'light' | 'dark' | null)
      : null) || 'light',
  activeModal: null,
  activeDrawer: null,
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
  setActiveTheme: (theme) => {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('theme', theme);
    }
    set({ activeTheme: theme });
  },
  openModal: (id) => set({ activeModal: id }),
  closeModal: () => set({ activeModal: null }),
  openDrawer: (id) => set({ activeDrawer: id }),
  closeDrawer: () => set({ activeDrawer: null }),
}));
