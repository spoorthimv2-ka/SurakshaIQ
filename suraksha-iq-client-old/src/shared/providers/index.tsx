import React, { useEffect, useMemo } from 'react';
import { QueryClient, QueryClientProvider, QueryCache, MutationCache } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import ErrorBoundary from './ErrorBoundary';
import { ThemeProvider } from './ThemeProvider';
import { ToastProvider } from './ToastProvider';
import { AuthProvider, useAuth } from 'shared/auth';
import { setAuthHandlers } from 'shared/api';
import type { ApiError } from 'shared/api';

function AuthHandlerBridge({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  useEffect(() => {
    setAuthHandlers({
      onUnauthorized: () => {
        void logout();
        navigate('/login', { replace: true });
      },
      onForbidden: () => {
        navigate('/forbidden', { replace: true });
      },
    });
  }, [logout, navigate]);

  return <>{children}</>;
}

function QueryProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const queryClient = useMemo(() => {
    const handleError = (error: unknown) => {
      const apiError = error as ApiError;
      if (apiError?.status === 401) {
        void logout();
        navigate('/login', { replace: true });
      } else if (apiError?.status === 403) {
        navigate('/forbidden', { replace: true });
      }
    };

    return new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 1000 * 60 * 5,
          gcTime: 1000 * 60 * 10,
          retry: (failureCount, error) => {
            const status = (error as unknown as ApiError)?.status;
            if (status === 401 || status === 403) return false;
            return failureCount < 1;
          },
        },
      },
      queryCache: new QueryCache({ onError: handleError }),
      mutationCache: new MutationCache({ onError: handleError }),
    });
  }, [logout, navigate]);

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

export const RouterProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <QueryProvider>
      <AuthHandlerBridge>{children}</AuthHandlerBridge>
    </QueryProvider>
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
