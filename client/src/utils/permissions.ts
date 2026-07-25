import type { Officer, UserRole } from 'shared/auth/types';

export type ModuleKey =
  | 'dashboard'
  | 'hotspots'
  | 'trends'
  | 'anomalies'
  | 'repeat-offenders'
  | 'network-analysis'
  | 'risk-scoring'
  | 'alerts'
  | 'reports'
  | 'admin'
  | 'crime-management'
  | 'fir-management'
  | 'search'
  | 'ai-investigation'
  | 'evidence-analyzer'
  | 'timeline'
  | 'ai-reports'
  | 'predictive-intelligence';

export interface NavItem {
  module: ModuleKey;
  label: string;
  path: string;
}

export const NAV_ITEMS: NavItem[] = [
  { module: 'dashboard', label: 'Dashboard', path: '/dashboard' },
  { module: 'hotspots', label: 'Hotspots', path: '/hotspots' },
  { module: 'trends', label: 'Trends', path: '/trends' },
  { module: 'anomalies', label: 'Anomalies', path: '/anomalies' },
  { module: 'repeat-offenders', label: 'Repeat Offenders', path: '/repeat-offenders' },
  { module: 'network-analysis', label: 'Network Analysis', path: '/network-analysis' },
  { module: 'risk-scoring', label: 'Risk Scoring', path: '/risk-scoring' },
  { module: 'predictive-intelligence', label: 'Predictive Intelligence', path: '/predictive-intelligence' },
  { module: 'alerts', label: 'Alerts', path: '/alerts' },
  { module: 'reports', label: 'Reports', path: '/reports' },
  { module: 'admin', label: 'Administration', path: '/admin' },
  { module: 'crime-management', label: 'Crime Management', path: '/crimes' },
  { module: 'fir-management', label: 'FIR Management', path: '/firs' },
  { module: 'ai-investigation', label: 'AI Investigation', path: '/ai-investigation' },
  { module: 'evidence-analyzer', label: 'Evidence Analyzer', path: '/evidence-analyzer' },
  { module: 'timeline', label: 'Timeline', path: '/timeline' },
  { module: 'ai-reports', label: 'AI Reports', path: '/ai-reports' },
];

export const MODULE_ROLES: Record<ModuleKey, UserRole[]> = {
  dashboard: [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'INVESTIGATING_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  hotspots: [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'INVESTIGATING_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  trends: [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  anomalies: [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  'repeat-offenders': [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'INVESTIGATING_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  'network-analysis': ['CID_ANALYST', 'SYSTEM_ADMINISTRATOR'],
  'risk-scoring': [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  'predictive-intelligence': [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  alerts: [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'INVESTIGATING_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  reports: [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  admin: ['SYSTEM_ADMINISTRATOR'],
  'crime-management': [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'INVESTIGATING_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  'fir-management': [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'INVESTIGATING_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  search: [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'INVESTIGATING_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  'ai-investigation': [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'INVESTIGATING_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  'evidence-analyzer': [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'INVESTIGATING_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  timeline: [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'INVESTIGATING_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
  'ai-reports': [
    'STATE_COMMAND',
    'RANGE_IG',
    'DISTRICT_SP',
    'STATION_HOUSE_OFFICER',
    'INVESTIGATING_OFFICER',
    'CID_ANALYST',
    'SYSTEM_ADMINISTRATOR',
  ],
};

export function hasRole(officer: Officer | null, ...roles: UserRole[]): boolean {
  if (!officer) return false;
  return roles.includes(officer.role);
}

export function hasPermission(officer: Officer | null, permission: string): boolean {
  if (!officer) return false;
  return officer.permissions.includes(permission);
}

export function canAccessModule(officer: Officer | null, module: ModuleKey): boolean {
  if (!officer) return false;
  return MODULE_ROLES[module].includes(officer.role);
}

export function canViewDistrict(officer: Officer | null, districtId: string): boolean {
  if (!officer) return false;

  const { role, jurisdiction } = officer;

  if (
    role === 'STATE_COMMAND' ||
    role === 'RANGE_IG' ||
    role === 'CID_ANALYST' ||
    role === 'SYSTEM_ADMINISTRATOR'
  ) {
    return true;
  }

  if (role === 'DISTRICT_SP') {
    return jurisdiction?.districtId === districtId;
  }

  return false;
}

export function canManageUsers(officer: Officer | null): boolean {
  return hasRole(officer, 'SYSTEM_ADMINISTRATOR') || hasPermission(officer, 'MANAGE_USERS');
}

export function getVisibleNavItems(officer: Officer | null): NavItem[] {
  return NAV_ITEMS.filter((item) => canAccessModule(officer, item.module));
}

export function getModuleForPath(pathname: string): ModuleKey | null {
  const match = NAV_ITEMS.find((item) => pathname === item.path || pathname.startsWith(`${item.path}/`));
  return match?.module ?? null;
}
