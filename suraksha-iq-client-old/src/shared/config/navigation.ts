import { UserRole } from 'shared/auth/types';

export interface NavItem {
  label: string;
  path: string;
  roles: UserRole[];
  icon?: string;
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', roles: ['STATE_COMMAND', 'RANGE_IG', 'DISTRICT_SP', 'STATION_OFFICER', 'INVESTIGATING_OFFICER', 'CID_ANALYST', 'ADMIN'] },
  { label: 'Hotspots', path: '/hotspots', roles: ['STATE_COMMAND', 'RANGE_IG', 'DISTRICT_SP', 'STATION_OFFICER', 'INVESTIGATING_OFFICER', 'CID_ANALYST', 'ADMIN'] },
  { label: 'Trends', path: '/trends', roles: ['STATE_COMMAND', 'RANGE_IG', 'DISTRICT_SP', 'STATION_OFFICER', 'CID_ANALYST', 'ADMIN'] },
  { label: 'Anomalies', path: '/anomalies', roles: ['STATE_COMMAND', 'RANGE_IG', 'DISTRICT_SP', 'CID_ANALYST', 'ADMIN'] },
  { label: 'Repeat Offenders', path: '/repeat-offenders', roles: ['STATE_COMMAND', 'RANGE_IG', 'DISTRICT_SP', 'STATION_OFFICER', 'INVESTIGATING_OFFICER', 'CID_ANALYST', 'ADMIN'] },
  { label: 'Network Analysis', path: '/network-analysis', roles: ['CID_ANALYST', 'ADMIN'] },
  { label: 'Risk Scoring', path: '/risk-scoring', roles: ['STATE_COMMAND', 'RANGE_IG', 'DISTRICT_SP', 'CID_ANALYST', 'ADMIN'] },
  { label: 'Alerts', path: '/alerts', roles: ['STATE_COMMAND', 'RANGE_IG', 'DISTRICT_SP', 'STATION_OFFICER', 'INVESTIGATING_OFFICER', 'CID_ANALYST', 'ADMIN'] },
  { label: 'Reports', path: '/reports', roles: ['STATE_COMMAND', 'RANGE_IG', 'DISTRICT_SP', 'STATION_OFFICER', 'CID_ANALYST', 'ADMIN'] },
  { label: 'Administration', path: '/admin', roles: ['ADMIN'] },
];

export function getVisibleNavItems(role: UserRole | undefined): NavItem[] {
  if (!role) return [];
  return NAV_ITEMS.filter((item) => item.roles.includes(role));
}

export function canAccessRoute(role: UserRole | undefined, path: string): boolean {
  const item = NAV_ITEMS.find((nav) => nav.path === path);
  if (!item) return true;
  return role ? item.roles.includes(role) : false;
}
