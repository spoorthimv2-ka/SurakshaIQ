export type UserRole =
  | 'STATION_HOUSE_OFFICER'
  | 'INVESTIGATING_OFFICER'
  | 'CID_ANALYST'
  | 'DISTRICT_SP'
  | 'STATE_COMMAND'
  | 'RANGE_IG'
  | 'SYSTEM_ADMINISTRATOR';

export type Jurisdiction = 'STATION' | 'DISTRICT' | 'STATE';

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
  district_id?: string;
  badge_number?: string;
  state_access?: boolean;
  token_version?: number;
}

export interface AuthContextType {
  user: Officer | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (badge_number: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (...roles: UserRole[]) => boolean;
}

export const ROLE_LABELS: Record<UserRole, string> = {
  STATION_HOUSE_OFFICER: 'Station House Officer',
  INVESTIGATING_OFFICER: 'Investigating Officer',
  CID_ANALYST: 'CID Analyst',
  DISTRICT_SP: 'District SP',
  STATE_COMMAND: 'State Command (DGP)',
  RANGE_IG: 'Range IG',
  SYSTEM_ADMINISTRATOR: 'System Administrator',
};

export const PII_PERMISSIONS = ['VIEW_PII'] as const;
