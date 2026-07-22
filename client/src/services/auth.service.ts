import { apiClient } from './api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  officer: Record<string, unknown>;
}

const TOKEN_KEY = 'access_token';
const OFFICER_KEY = 'officer';

function getStoredToken(): string | null {
  if (typeof localStorage === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

function getStoredOfficer(): Record<string, unknown> | null {
  if (typeof localStorage === 'undefined') return null;
  const raw = localStorage.getItem(OFFICER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function setStoredSession(token: string, officer: Record<string, unknown>): void {
  if (typeof localStorage === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(OFFICER_KEY, JSON.stringify(officer));
}

function clearStoredSession(): void {
  if (typeof localStorage === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(OFFICER_KEY);
}

export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', { email, password });
    const { access_token, officer } = response.data;
    setStoredSession(access_token, officer);
    return response.data;
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch {
    } finally {
      clearStoredSession();
    }
  },

  async getCurrentUser(): Promise<Record<string, unknown> | null> {
    const token = getStoredToken();
    if (!token) return null;
    try {
      const response = await apiClient.get<{ data: Record<string, unknown> }>('/auth/me');
      const officer = response.data.data;
      setStoredSession(token, officer);
      return officer;
    } catch {
      clearStoredSession();
      return null;
    }
  },

  getStoredOfficer(): Record<string, unknown> | null {
    return getStoredOfficer();
  },

  getStoredToken(): string | null {
    return getStoredToken();
  },

  clearStorage(): void {
    clearStoredSession();
  },
};