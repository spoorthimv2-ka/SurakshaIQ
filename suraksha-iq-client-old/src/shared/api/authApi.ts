import apiClient from './client';
import { enableMockMode } from 'config/env';
import { Officer, SessionData, UserRole } from 'shared/auth/types';

export interface LoginResponse {
  userId: string;
  mfaRequired: boolean;
}

export interface AuthResponse {
  token: string;
  officer: Officer;
}

const MOCK_USERS: Record<string, { password: string; officer: Officer; mfaRequired: boolean }> = {
  'dgp@karnataka.gov.in': {
    password: 'demo1234',
    mfaRequired: true,
    officer: {
      id: 'off-001',
      name: 'Dr. Rajesh Kumar',
      email: 'dgp@karnataka.gov.in',
      rank: 'DGP',
      designation: 'Director General of Police',
      role: 'STATE_COMMAND',
      jurisdiction: { type: 'STATE' },
      permissions: ['view:pii', 'export:reports', 'manage:alerts'],
      mfaRequired: true,
      mfaVerified: false,
    },
  },
  'admin@karnataka.gov.in': {
    password: 'admin1234',
    mfaRequired: true,
    officer: {
      id: 'off-007',
      name: 'Priya Sharma',
      email: 'admin@karnataka.gov.in',
      rank: 'System Admin',
      designation: 'System Administrator',
      role: 'ADMIN',
      jurisdiction: { type: 'STATE' },
      permissions: ['view:pii', 'export:reports', 'manage:users', 'manage:alert-rules'],
      mfaRequired: true,
      mfaVerified: false,
    },
  },
};

function createMockToken(officer: Officer): string {
  return btoa(JSON.stringify({ sub: officer.id, role: officer.role, exp: Date.now() + 3600000 }));
}

export const authApi = {
  login: async (email: string, password: string) => {
    if (enableMockMode) {
      const user = MOCK_USERS[email.toLowerCase()];
      if (!user || user.password !== password) {
        throw { status: 401, title: 'Unauthorized', message: 'Invalid credentials', type: 'auth/invalid' };
      }
      sessionStorage.setItem('pending_mfa_user', user.officer.id);
      return {
        data: {
          data: { userId: user.officer.id, mfaRequired: user.mfaRequired } satisfies LoginResponse,
        },
      };
    }
    return apiClient.post<{ data: LoginResponse }>('/auth/login', { email, password });
  },

  mfaChallenge: async (userId: string, code: string) => {
    if (enableMockMode) {
      const pendingId = sessionStorage.getItem('pending_mfa_user');
      const user = Object.values(MOCK_USERS).find((u) => u.officer.id === userId || u.officer.id === pendingId);
      if (!user || code.length !== 6) {
        throw { status: 401, title: 'Unauthorized', message: 'Invalid MFA code', type: 'auth/mfa-failed' };
      }
      const officer: Officer = { ...user.officer, mfaVerified: true };
      const token = createMockToken(officer);
      sessionStorage.removeItem('pending_mfa_user');
      return {
        data: {
          data: { token, officer } satisfies AuthResponse,
        },
      };
    }
    return apiClient.post<{ data: AuthResponse }>('/auth/mfa-challenge', { userId, code });
  },

  logout: async () => {
    if (enableMockMode) {
      return { data: { data: null } };
    }
    return apiClient.post('/auth/logout');
  },

  refreshToken: async () => {
    if (enableMockMode) {
      const sessionRaw = sessionStorage.getItem('auth_session');
      if (!sessionRaw) throw new Error('No session');
      const session: SessionData = JSON.parse(sessionRaw);
      return { data: { data: { token: session.token } } };
    }
    return apiClient.post<{ data: { token: string } }>('/auth/refresh');
  },

  reauthenticate: async (password: string) => {
    if (enableMockMode) {
      return { data: { data: { verified: password.length >= 4 } } };
    }
    return apiClient.post<{ data: { verified: boolean } }>('/auth/reauthenticate', { password });
  },
};

export type { UserRole };
