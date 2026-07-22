import React, { createContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { authService } from 'services/auth.service';
import type { Officer, AuthContextType, UserRole } from 'shared/auth/types';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

function mapBackendOfficerToOfficer(data: Record<string, unknown>): Officer {
  const role = String(data.role || 'STATION_HOUSE_OFFICER') as UserRole;
  const permissions = Array.isArray(data.permissions) ? data.permissions.map(String) : [];
  const stationId = data.station_id ? String(data.station_id) : undefined;

  return {
    id: String(data.ROWID || data.id || ''),
    name: String(data.name || ''),
    email: String(data.email || ''),
    rank: '',
    designation: '',
    role,
    jurisdiction: stationId ? { type: 'STATION', stationId } : { type: 'STATION' },
    permissions,
    ROWID: data.ROWID ? String(data.ROWID) : undefined,
    user_id: data.user_id ? String(data.user_id) : undefined,
    station_id: stationId,
  };
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<Officer | null>(null);
  const [token, setToken] = useState<string | null>(() => authService.getStoredToken());
  const [loading, setLoading] = useState<boolean>(true);


  const refreshSession = useCallback(async () => {
    setLoading(true);
    try {
      const storedOfficer = authService.getStoredOfficer();
      if (storedOfficer) {
        const mapped = mapBackendOfficerToOfficer(storedOfficer);
        setUser(mapped);
      }

      const freshOfficer = await authService.getCurrentUser();
      if (freshOfficer) {
        const mapped = mapBackendOfficerToOfficer(freshOfficer);
        setUser(mapped);
        setToken(authService.getStoredToken());
      } else {
        setUser(null);
        setToken(null);
      }
    } catch {
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshSession();
  }, [refreshSession]);

  const login = useCallback(async (email: string, password: string) => {
    const response = await authService.login(email, password);
    const mapped = mapBackendOfficerToOfficer(response.officer);
    setUser(mapped);
    setToken(response.access_token);
  }, []);

  const logout = useCallback(async () => {
    await authService.logout();
    setUser(null);
    setToken(null);
    window.location.href = "/login"
  },[]);

  const hasPermission = useCallback(
    (permission: string): boolean => {
      return user?.permissions.includes(permission) ?? false;
    },
    [user]
  );

  const hasRole = useCallback(
    (...roles: UserRole[]): boolean => {
      if (!user) return false;
      return roles.includes(user.role);
    },
    [user]
  );

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    loading,
    login,
    logout,
    refreshSession,
    hasPermission,
    hasRole,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
