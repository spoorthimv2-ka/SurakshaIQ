import React, { Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RootLayout, AuthLayout, AppShellLayout, DashboardLayout } from 'app/layouts';
import { RequireAuth } from 'shared/auth';
import { LoadingSkeleton } from 'shared/components';

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
        path: 'mfa-challenge',
        element: <AuthLayout />,
        children: [
          { index: true, element: lazy(() => import('features/authentication/pages/MFAChallenge')) },
        ],
      },
      {
        element: <RequireAuth />,
        children: [
          {
            element: <AppShellLayout />,
            children: [
              {
                path: 'dashboard',
                element: <DashboardLayout />,
                children: [
                  { index: true, element: lazy(() => import('features/dashboard/pages/Dashboard')) },
                ],
              },
              { path: 'hotspots', element: lazy(() => import('features/hotspots/pages/Hotspots')) },
              { path: 'trends', element: lazy(() => import('features/trends/pages/Trends')) },
              { path: 'anomalies', element: lazy(() => import('features/anomalies/pages/Anomalies')) },
              {
                path: 'repeat-offenders',
                element: lazy(() => import('features/repeat-offenders/pages/RepeatOffenders')),
              },
              {
                element: <RequireAuth roles={['CID_ANALYST', 'ADMIN']} />,
                children: [
                  {
                    path: 'network-analysis',
                    element: lazy(() => import('features/network-analysis/pages/NetworkAnalysis')),
                  },
                ],
              },
              { path: 'risk-scoring', element: lazy(() => import('features/risk-scoring/pages/RiskScoring')) },
              { path: 'alerts', element: lazy(() => import('features/alerts/pages/Alerts')) },
              { path: 'reports', element: lazy(() => import('features/reports/pages/Reports')) },
              {
                path: 'district/:districtId',
                element: lazy(() => import('features/district-comparison/pages/DistrictDetail')),
              },
              {
                element: <RequireAuth roles={['ADMIN']} />,
                children: [{ path: 'admin', element: lazy(() => import('features/admin/pages/Admin')) }],
              },
            ],
          },
        ],
      },
      { path: 'forbidden', element: lazy(() => import('features/errors/pages/Forbidden')) },
      { path: '*', element: lazy(() => import('features/errors/pages/NotFound')) },
    ],
  },
]);
