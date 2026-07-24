import React, { Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RootLayout, AuthLayout, AppShellLayout, DashboardLayout } from 'app/layouts';
import { ProtectedRoute, RoleProtectedRoute } from 'routes';
import { LoadingSkeleton } from 'shared/components';
import { MODULE_ROLES } from 'utils/permissions';

const LoadingState = () => (
  <div className="flex min-h-screen items-center justify-center">
    <LoadingSkeleton variant="page" />
  </div>
);

const lazy = (factory: () => Promise<{ default: React.ComponentType }>) => {
  const Component = React.lazy(factory);
  return (
    <Suspense fallback={<LoadingState />}>
      <Component />
    </Suspense>
  );
};

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      {
        path: 'login',
        element: <AuthLayout />,
        children: [{ index: true, element: lazy(() => import('features/authentication/pages/Login')) }],
      },
      {
        element: <ProtectedRoute />,
        children: [
          {
            element: <AppShellLayout />,
            children: [
              {
                element: <RoleProtectedRoute roles={MODULE_ROLES.dashboard} />,
                children: [
                  {
                    path: 'dashboard',
                    element: <DashboardLayout />,
                    children: [
                      { index: true, element: lazy(() => import('features/dashboard/pages/Dashboard')) },
                    ],
                  },
                ],
              },
              {
                element: <RoleProtectedRoute roles={MODULE_ROLES.hotspots} />,
                children: [{ path: 'hotspots', element: lazy(() => import('features/hotspots/pages/Hotspots')) }],
              },
              {
                element: <RoleProtectedRoute roles={MODULE_ROLES.trends} />,
                children: [{ path: 'trends', element: lazy(() => import('features/trends/pages/Trends')) }],
              },
              {
                element: <RoleProtectedRoute roles={MODULE_ROLES.anomalies} />,
                children: [{ path: 'anomalies', element: lazy(() => import('features/anomalies/pages/Anomalies')) }],
              },
              {
                element: <RoleProtectedRoute roles={MODULE_ROLES['repeat-offenders']} />,
                children: [
                  {
                    path: 'repeat-offenders',
                    element: lazy(() => import('features/repeat-offenders/pages/RepeatOffenders')),
                  },
                ],
              },
              {
                element: <RoleProtectedRoute roles={MODULE_ROLES['network-analysis']} />,
                children: [
                  {
                    path: 'network-analysis',
                    element: lazy(() => import('features/network-analysis/pages/NetworkAnalysis')),
                  },
                ],
              },
              {
                element: <RoleProtectedRoute roles={MODULE_ROLES['risk-scoring']} />,
                children: [
                  { path: 'risk-scoring', element: lazy(() => import('features/risk-scoring/pages/RiskScoring')) },
                ],
              },
               {
                 element: <RoleProtectedRoute roles={MODULE_ROLES.alerts} />,
                 children: [{ path: 'alerts', element: lazy(() => import('features/alerts/pages/Alerts')) }],
               },
               {
                 element: <RoleProtectedRoute roles={MODULE_ROLES.reports} />,
                 children: [{ path: 'reports', element: lazy(() => import('features/reports/pages/Reports')) }],
               },
               {
                 path: 'search',
                 element: lazy(() => import('features/search/pages/Search')),
               },
               {
                 element: <RoleProtectedRoute roles={MODULE_ROLES.admin} />,
                 children: [{ path: 'admin', element: lazy(() => import('features/admin/pages/Admin')) }],
               },
              {
                element: <RoleProtectedRoute roles={MODULE_ROLES['crime-management']} />,
                children: [{ path: 'crimes', element: lazy(() => import('features/crime-management/pages/CrimeManagement')) }],
              },
              {
                element: <RoleProtectedRoute roles={MODULE_ROLES['fir-management']} />,
                children: [{ path: 'firs', element: lazy(() => import('features/fir-management/pages/FirManagement')) }],
              },
              {
                path: 'district/:districtId',
                element: lazy(() => import('features/district-comparison/pages/DistrictDetail')),
              },
            ],
          },
        ],
      },
      { path: 'unauthorized', element: lazy(() => import('features/errors/pages/Unauthorized')) },
      { path: 'forbidden', element: <Navigate to="/unauthorized" replace /> },
      { path: '*', element: lazy(() => import('features/errors/pages/NotFound')) },
    ],
  },
], {
  // Vite's BASE_URL is automatically derived from vite.config.ts `base`.
  // This keeps React Router's basename in sync with the deployed subpath.
  basename: import.meta.env.BASE_URL || '/',
});