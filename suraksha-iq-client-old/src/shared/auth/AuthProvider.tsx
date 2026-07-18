import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import { authApi } from 'shared/api';
import { Officer, AuthContextType, UserRole, SessionData } from './types';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

let memoryToken: string | null = null;

export function getMemoryToken(): string | null {
  return memoryToken;
}

export function setMemoryToken(token: string | null): void {
  memoryToken = token;
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [officer, setOfficer] = useState<Officer | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const pendingUserId = useRef<string | null>(null);

  useEffect(() => {
    const sessionData = sessionStorage.getItem('auth_session');
    if (sessionData) {
      try {
        const data: SessionData = JSON.parse(sessionData);
        if (data.expiresAt > Date.now()) {
          setOfficer(data.officer);
          setMemoryToken(data.token);
          sessionStorage.setItem('auth_token', data.token);
        } else {
          sessionStorage.removeItem('auth_session');
          sessionStorage.removeItem('auth_token');
          setMemoryToken(null);
        }
      } catch {
        sessionStorage.removeItem('auth_session');
        sessionStorage.removeItem('auth_token');
        setMemoryToken(null);
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await authApi.login(email, password);
      const result = response.data.data;
      pendingUserId.current = result.userId;
      return { userId: result.userId, mfaRequired: result.mfaRequired };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const mfaChallenge = useCallback(async (userId: string, code: string) => {
    setIsLoading(true);
    try {
      const response = await authApi.mfaChallenge(userId, code);
      const { token, officer: authenticatedOfficer } = response.data.data;
      const sessionData: SessionData = {
        officer: authenticatedOfficer,
        token,
        expiresAt: Date.now() + 8 * 60 * 60 * 1000,
      };
      setMemoryToken(token);
      sessionStorage.setItem('auth_session', JSON.stringify(sessionData));
      sessionStorage.setItem('auth_token', token);
      setOfficer(authenticatedOfficer);
      pendingUserId.current = null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await authApi.logout();
    } finally {
      sessionStorage.removeItem('auth_session');
      sessionStorage.removeItem('auth_token');
      sessionStorage.removeItem('pending_mfa_user');
      setMemoryToken(null);
      setOfficer(null);
      pendingUserId.current = null;
      setIsLoading(false);
    }
  }, []);

  const reauthenticate = useCallback(async (password: string): Promise<boolean> => {
    try {
      const response = await authApi.reauthenticate(password);
      return response.data.data.verified;
    } catch {
      return false;
    }
  }, []);

  const hasPermission = useCallback(
    (permission: string): boolean => officer?.permissions.includes(permission) ?? false,
    [officer]
  );

  const hasRole = useCallback(
    (...roles: UserRole[]): boolean => (officer ? roles.includes(officer.role) : false),
    [officer]
  );

  const getPendingUserId = useCallback((): string | null => pendingUserId.current, []);

  const value: AuthContextType = {
    officer,
    isAuthenticated: !!officer,
    isLoading,
    login,
    mfaChallenge,
    logout,
    reauthenticate,
    hasPermission,
    hasRole,
    getPendingUserId,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
