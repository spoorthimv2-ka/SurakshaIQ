import React, { Suspense } from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RootLayout, AuthLayout, AppShellLayout, DashboardLayout } from 'app/layouts';
import { ProtectedRoute } from 'routes';
import { LoadingSkeleton } from 'shared/components';
import { canAccessModule, type ModuleKey } from 'utils/permissions';
import { useAuth } from 'hooks/useAuth';
import { Outlet } from 'react-router-dom';

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

function PermissionRoute({ module }: { module: ModuleKey }) {
  const { user } = useAuth();
  if (!canAccessModule(user, module)) {
    return <Navigate to="/unauthorized" replace />;
  }
  return <Outlet />;
}

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
                element: <PermissionRoute module="dashboard" />,
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
                element: <PermissionRoute module="hotspots" />,
                children: [{ path: 'hotspots', element: lazy(() => import('features/hotspots/pages/Hotspots')) }],
              },
              {
                element: <PermissionRoute module="trends" />,
                children: [{ path: 'trends', element: lazy(() => import('features/trends/pages/Trends')) }],
              },
              {
                element: <PermissionRoute module="anomalies" />,
                children: [{ path: 'anomalies', element: lazy(() => import('features/anomalies/pages/Anomalies')) }],
              },
              {
                element: <PermissionRoute module="repeat-offenders" />,
                children: [
                  {
                    path: 'repeat-offenders',
                    element: lazy(() => import('features/repeat-offenders/pages/RepeatOffenders')),
                  },
                ],
              },
              {
                element: <PermissionRoute module="network-analysis" />,
                children: [
                  {
                    path: 'network-analysis',
                    element: lazy(() => import('features/network-analysis/pages/NetworkAnalysis')),
                  },
                ],
              },
              {
                element: <PermissionRoute module="risk-scoring" />,
                children: [
                  { path: 'risk-scoring', element: lazy(() => import('features/risk-scoring/pages/RiskScoring')) },
                ],
              },
               {
                 element: <PermissionRoute module="alerts" />,
                 children: [{ path: 'alerts', element: lazy(() => import('features/alerts/pages/Alerts')) }],
               },
               {
                 element: <PermissionRoute module="reports" />,
                 children: [{ path: 'reports', element: lazy(() => import('features/reports/pages/Reports')) }],
               },
               {
                 path: 'search',
                 element: lazy(() => import('features/search/pages/Search')),
               },
                {
                   element: <PermissionRoute module="admin" />,
                   children: [{ path: 'admin', element: lazy(() => import('features/admin/pages/Admin')) }],
                 },
                 {
                   element: <PermissionRoute module="timeline" />,
                   children: [{ path: 'timeline', element: lazy(() => import('features/timeline/pages/Timeline')) }],
                 },
              {
                element: <PermissionRoute module="crime-management" />,
                children: [{ path: 'crimes', element: lazy(() => import('features/crime-management/pages/CrimeManagement')) }],
              },
               {
                 element: <PermissionRoute module="fir-management" />,
                 children: [{ path: 'firs', element: lazy(() => import('features/fir-management/pages/FirManagement')) }],
               },
               {
                 element: <PermissionRoute module="ai-investigation" />,
                 children: [{ path: 'ai-investigation', element: lazy(() => import('features/ai-investigation/pages/AiInvestigation')) }],
               },
               {
                 element: <PermissionRoute module="evidence-analyzer" />,
                 children: [{ path: 'evidence-analyzer', element: lazy(() => import('features/evidence-analyzer/pages/EvidenceAnalyzer')) }],
               },
                {
                  element: <PermissionRoute module="risk-scoring" />,
                  children: [{ path: 'risk-scoring', element: lazy(() => import('features/risk-scoring/pages/RiskScoring')) }],
                },
                {
                  element: <PermissionRoute module="predictive-intelligence" />,
                  children: [{ path: 'predictive-intelligence', element: lazy(() => import('features/predictive-intelligence/pages/PredictiveIntelligence')) }],
                },
                {
                  element: <PermissionRoute module="settings" />,
                  children: [{ path: 'settings', element: lazy(() => import('features/settings/pages/Settings')) }],
                },
                {
                  element: <PermissionRoute module="notifications" />,
                  children: [{ path: 'notifications', element: lazy(() => import('features/settings/pages/Notifications')) }],
                },
               {
                 element: <PermissionRoute module="ai-reports" />,
                 children: [{ path: 'ai-reports', element: lazy(() => import('features/ai-reports/pages/AiReports')) }],
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