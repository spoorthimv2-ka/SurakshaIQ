import React from 'react';
import { useAuth } from './AuthProvider';
import { UserRole, PII_PERMISSIONS } from './types';

interface RoleGateProps {
  children: React.ReactNode;
  roles?: UserRole[];
  permissions?: string[];
  requirePii?: boolean;
  fallback?: React.ReactNode;
  redacted?: React.ReactNode;
}

export const RoleGate: React.FC<RoleGateProps> = ({
  children,
  roles,
  permissions,
  requirePii = false,
  fallback = null,
  redacted = <span className="text-gov-slate italic">[Redacted]</span>,
}) => {
  const { hasRole, hasPermission, officer } = useAuth();

  if (!officer) {
    return <>{fallback}</>;
  }

  if (roles && !hasRole(...roles)) {
    return <>{fallback}</>;
  }

  if (permissions && !permissions.every((p) => hasPermission(p))) {
    return <>{fallback}</>;
  }

  if (requirePii && !PII_PERMISSIONS.some((p) => hasPermission(p))) {
    return <>{redacted}</>;
  }

  return <>{children}</>;
};
