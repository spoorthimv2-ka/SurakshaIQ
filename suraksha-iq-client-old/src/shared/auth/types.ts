export type UserRole =
  | 'STATE_COMMAND'
  | 'RANGE_IG'
  | 'DISTRICT_SP'
  | 'STATION_OFFICER'
  | 'INVESTIGATING_OFFICER'
  | 'CID_ANALYST'
  | 'ADMIN';

export type Jurisdiction = 'STATE' | 'RANGE' | 'DISTRICT' | 'STATION';

export interface Officer {
  id: string;
  name: string;
  email: string;
  rank: string;
  designation: string;
  role: UserRole;
  jurisdiction: {
    type: Jurisdiction;
    stationId?: string;
    districtId?: string;
    rangeId?: string;
  };
  permissions: string[];
  mfaRequired: boolean;
  mfaVerified: boolean;
}

export interface AuthContextType {
  officer: Officer | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ userId: string; mfaRequired: boolean }>;
  mfaChallenge: (userId: string, code: string) => Promise<void>;
  logout: () => Promise<void>;
  reauthenticate: (password: string) => Promise<boolean>;
  hasPermission: (permission: string) => boolean;
  hasRole: (...roles: UserRole[]) => boolean;
  getPendingUserId: () => string | null;
}

export interface SessionData {
  officer: Officer;
  token: string;
  expiresAt: number;
}

export const ROLE_LABELS: Record<UserRole, string> = {
  STATE_COMMAND: 'State Command (DGP)',
  RANGE_IG: 'Range IG',
  DISTRICT_SP: 'District SP',
  STATION_OFFICER: 'Station House Officer',
  INVESTIGATING_OFFICER: 'Investigating Officer',
  CID_ANALYST: 'CID Analyst',
  ADMIN: 'System Administrator',
};

export const PII_PERMISSIONS = ['view:pii', 'view:victim', 'view:accused', 'view:juvenile'] as const;
