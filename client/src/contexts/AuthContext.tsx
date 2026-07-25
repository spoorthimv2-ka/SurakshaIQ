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
  const districtId = data.district_id ? String(data.district_id) : undefined;
  const jurisdictionType = String(data.jurisdiction_type || 'STATION') as 'STATION' | 'DISTRICT' | 'STATE';

  return {
    id: String(data.ROWID || data.id || ''),
    name: String(data.name || ''),
    email: String(data.email || ''),
    rank: '',
    designation: '',
    role,
    jurisdiction: { type: jurisdictionType, stationId, districtId },
    permissions,
    ROWID: data.ROWID ? String(data.ROWID) : undefined,
    user_id: data.user_id ? String(data.user_id) : undefined,
    station_id: stationId,
    district_id: districtId,
    badge_number: data.badge_number ? String(data.badge_number) : undefined,
    state_access: data.state_access === true,
    token_version: data.token_version ? Number(data.token_version) : 1,
  };
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<Officer | null>(null);
  const [token, setToken] = useState<string | null>(() => authService.getStoredToken());
  const [loading, setLoading] = useState<boolean>(true);

  const refreshSession = useCallback(async () => {
    setLoading(true);
    try {
      const storedToken = authService.getStoredToken();
      if (!storedToken) {
        setUser(null);
        setToken(null);
        return;
      }

      const freshOfficer = await authService.getCurrentUser();
      if (freshOfficer) {
        const mapped = mapBackendOfficerToOfficer(freshOfficer);
        setUser(mapped);
        setToken(storedToken);
      } else {
        setUser(null);
        setToken(null);
        authService.clearStorage();
      }
    } catch {
      setUser(null);
      setToken(null);
      authService.clearStorage();
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshSession();
  }, [refreshSession]);

  const login = useCallback(async (badge_number: string, password: string) => {
    const response = await authService.login(badge_number, password);
    const mapped = mapBackendOfficerToOfficer(response.officer);
    setUser(mapped);
    setToken(response.access_token);
  }, []);

  const logout = useCallback(async () => {
    await authService.logout();
    setUser(null);
    setToken(null);
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
