import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './AuthProvider';
import { UserRole } from './types';
import { LoadingSkeleton } from 'shared/components';

interface RequireAuthProps {
  children?: React.ReactNode;
  roles?: UserRole[];
}

export const RequireAuth: React.FC<RequireAuthProps> = ({ children, roles }) => {
  const { isAuthenticated, officer, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gov-slate/5">
        <LoadingSkeleton variant="page" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (roles && officer && !roles.includes(officer.role)) {
    return <Navigate to="/forbidden" replace />;
  }

  return children ? <>{children}</> : <Outlet />;
};

export default RequireAuth;
