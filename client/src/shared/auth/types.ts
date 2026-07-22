export type UserRole =
  | 'STATE_COMMAND'
  | 'RANGE_IG'
  | 'DISTRICT_SP'
  | 'STATION_HOUSE_OFFICER'
  | 'INVESTIGATING_OFFICER'
  | 'CID_ANALYST'
  | 'SYSTEM_ADMINISTRATOR';

export type Jurisdiction = 'STATE' | 'RANGE' | 'DISTRICT' | 'STATION';

export interface Officer {
  id: string;
  name: string;
  email: string;
  rank?: string;
  designation?: string;
  role: UserRole;
  jurisdiction?: {
    type: Jurisdiction;
    stationId?: string;
    districtId?: string;
    rangeId?: string;
  };
  permissions: string[];
  ROWID?: string;
  user_id?: string;
  station_id?: string;
}

export interface AuthContextType {
  user: Officer | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (...roles: UserRole[]) => boolean;
}

export const ROLE_LABELS: Record<UserRole, string> = {
  STATE_COMMAND: 'State Command (DGP)',
  RANGE_IG: 'Range IG',
  DISTRICT_SP: 'District SP',
  STATION_HOUSE_OFFICER: 'Station House Officer',
  INVESTIGATING_OFFICER: 'Investigating Officer',
  CID_ANALYST: 'CID Analyst',
  SYSTEM_ADMINISTRATOR: 'System Administrator',
};

export const PII_PERMISSIONS = ['VIEW_PII'] as const;
