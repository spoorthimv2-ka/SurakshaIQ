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
  /**
   * Authenticates an officer using email and password against the backend JWT endpoint.
   */
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', { email, password });
    const { access_token, officer } = response.data;
    setStoredSession(access_token, officer);
    return response.data;
  },

  /**
   * Logs out the current officer session.
   * Clears local storage and calls the backend logout endpoint.
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch {
      // ignore logout endpoint errors - we still clear local state
    } finally {
      clearStoredSession();
    }
  },

  /**
   * Retrieves the current officer profile from the backend using the stored JWT.
   * Returns null if no token is present or the request fails.
   */
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

  /**
   * Returns the cached officer object from localStorage without making a network request.
   */
  getStoredOfficer(): Record<string, unknown> | null {
    return getStoredOfficer();
  },

  /**
   * Returns the stored JWT access token.
   */
  getStoredToken(): string | null {
    return getStoredToken();
  },
};
