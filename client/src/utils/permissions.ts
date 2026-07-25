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
  | 'predictive-intelligence'
  | 'settings'
  | 'notifications';

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
  { module: 'settings', label: 'Settings', path: '/settings' },
  { module: 'notifications', label: 'Notifications', path: '/notifications' },
];

const TIER_PERMISSIONS: Record<string, string[]> = {
  OFFICER: [
    'access_dashboard',
    'access_fir_management',
    'access_alerts',
    'access_crime_management',
    'access_repeat_offenders',
    'access_search',
    'access_ai_investigation',
    'access_evidence_analyzer',
    'access_timeline',
    'access_ai_reports',
    'access_settings',
    'access_notifications',
    'access_hotspots',
  ],
  INSPECTOR: [
    'access_trends',
    'access_anomalies',
    'access_network_analysis',
    'access_risk_scoring',
    'access_predictive_intelligence',
    'access_reports',
    'access_district_analytics',
  ],
  DSP: [
    'access_alert_threshold_config',
  ],
  SP: [
    'access_state_analytics',
  ],
  ADMIN: [
    'access_admin',
    'access_master_data',
    'access_user_management',
    'access_role_assignment',
    'access_jurisdiction_assignment',
    'access_system_configuration',
    'view_pii',
  ],
};

const ROLE_TIER_MAP: Record<UserRole, string> = {
  STATION_HOUSE_OFFICER: 'OFFICER',
  INVESTIGATING_OFFICER: 'OFFICER',
  CID_ANALYST: 'INSPECTOR',
  DISTRICT_SP: 'DSP',
  STATE_COMMAND: 'SP',
  RANGE_IG: 'SP',
  SYSTEM_ADMINISTRATOR: 'ADMIN',
};

function tierForRole(role: UserRole): string {
  return ROLE_TIER_MAP[role] || 'OFFICER';
}

function permissionsForTier(tier: string): string[] {
  const base = TIER_PERMISSIONS[tier] || [];
  if (tier === 'ADMIN') return base;
  const higher = ['OFFICER', 'INSPECTOR', 'DSP', 'SP', 'ADMIN'];
  const idx = higher.indexOf(tier);
  let inherited: string[] = [];
  for (let i = 0; i < idx; i++) {
    inherited = inherited.concat(TIER_PERMISSIONS[higher[i]] || []);
  }
  return [...new Set([...base, ...inherited])];
}

export function hasPermission(officer: Officer | null, permission: string): boolean {
  if (!officer) return false;
  const tier = tierForRole(officer.role);
  const perms = permissionsForTier(tier);
  return perms.includes(permission);
}

export function hasRole(officer: Officer | null, ...roles: UserRole[]): boolean {
  if (!officer) return false;
  return roles.includes(officer.role);
}

export function canAccessModule(officer: Officer | null, module: ModuleKey): boolean {
  if (!officer) return false;
  const permissionMap: Record<ModuleKey, string> = {
    dashboard: 'access_dashboard',
    hotspots: 'access_hotspots',
    trends: 'access_trends',
    anomalies: 'access_anomalies',
    'repeat-offenders': 'access_repeat_offenders',
    'network-analysis': 'access_network_analysis',
    'risk-scoring': 'access_risk_scoring',
    'predictive-intelligence': 'access_predictive_intelligence',
    alerts: 'access_alerts',
    reports: 'access_reports',
    admin: 'access_admin',
    'crime-management': 'access_crime_management',
    'fir-management': 'access_fir_management',
    search: 'access_search',
    'ai-investigation': 'access_ai_investigation',
    'evidence-analyzer': 'access_evidence_analyzer',
    timeline: 'access_timeline',
    'ai-reports': 'access_ai_reports',
    settings: 'access_settings',
    notifications: 'access_notifications',
  };
  const required = permissionMap[module];
  if (!required) return false;
  return hasPermission(officer, required);
}

export function canViewDistrict(officer: Officer | null, districtId: string): boolean {
  if (!officer) return false;
  const { role, jurisdiction } = officer;
  if (['SYSTEM_ADMINISTRATOR', 'STATE_COMMAND', 'RANGE_IG', 'CID_ANALYST'].includes(role)) {
    return true;
  }
  if (role === 'DISTRICT_SP') {
    return jurisdiction?.districtId === districtId;
  }
  return false;
}

export function canManageUsers(officer: Officer | null): boolean {
  return hasPermission(officer, 'access_user_management');
}

export function getVisibleNavItems(officer: Officer | null): NavItem[] {
  return NAV_ITEMS.filter((item) => canAccessModule(officer, item.module));
}

export function getModuleForPath(pathname: string): ModuleKey | null {
  const match = NAV_ITEMS.find((item) => pathname === item.path || pathname.startsWith(`${item.path}/`));
  return match?.module ?? null;
}

