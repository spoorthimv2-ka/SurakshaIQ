import React, { useEffect } from 'react';
import { QueryClient, QueryClientProvider, QueryCache, MutationCache } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import ErrorBoundary from './ErrorBoundary';
import { ThemeProvider } from './ThemeProvider';
import { ToastProvider } from './ToastProvider';
import { AuthProvider, useAuth } from 'shared/auth';
import type { AxiosError } from 'services/api';
import { registerSessionLifecycle, handleForbidden, handleUnauthorized } from 'utils/sessionLifecycle';

function SessionLifecycleRegistrar({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  useEffect(() => {
    return registerSessionLifecycle({
      onUnauthorized: () => {
        logout();
        navigate('/login', { replace: true });
      },
      onForbidden: () => {
        navigate('/unauthorized', { replace: true });
      },
    });
  }, [logout, navigate]);

  return <>{children}</>;
}

function QueryProvider({ children }: { children: React.ReactNode }) {
  const queryClient = React.useMemo(() => {
    const handleError = (error: unknown) => {
      const status = (error as AxiosError).response?.status;
      if (status === 401) {
        console.groupCollapsed('[REACT QUERY] 401 Unauthorized');
        console.log('Error:', error);
        console.log('Response status:', status);
        console.log('Response data:', (error as AxiosError).response?.data);
        console.log('VITE_DEV_SKIP_AUTH:', import.meta.env.VITE_DEV_SKIP_AUTH);
        console.groupEnd();
        handleUnauthorized();
      } else if (status === 403) {
        handleForbidden();
      }
    };

    return new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 1000 * 60 * 5,
          gcTime: 1000 * 60 * 10,
          retry: (failureCount, error) => {
            const status = (error as unknown as AxiosError).response?.status;
            if (status === 401 || status === 403) return false;
            return failureCount < 1;
          },
          refetchOnWindowFocus: false,
        },
        mutations: {
          retry: false,
        },
      },
      queryCache: new QueryCache({ onError: handleError }),
      mutationCache: new MutationCache({ onError: handleError }),
    });
  }, []);

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

export const RouterProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <SessionLifecycleRegistrar>
      <QueryProvider>{children}</QueryProvider>
    </SessionLifecycleRegistrar>
  );
};

export const Providers: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <ThemeProvider>
          <ToastProvider>{children}</ToastProvider>
        </ThemeProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
};
