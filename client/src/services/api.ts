import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';
import { apiBaseUrl, apiTimeout } from 'config/env';
import { handleForbidden, handleUnauthorized } from 'utils/sessionLifecycle';

export const apiClient: AxiosInstance = axios.create({
  baseURL: apiBaseUrl,
  timeout: apiTimeout,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (typeof localStorage !== 'undefined' && config.headers) {
    if (import.meta.env.VITE_DEV_SKIP_AUTH === 'true') {
      return config;
    }
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status;
    if (status === 401) {
      console.groupCollapsed('[API INTERCEPTOR] 401 Unauthorized');
      console.log('URL:', error.config?.url);
      console.log('Method:', error.config?.method);
      console.log('BaseURL:', error.config?.baseURL);
      console.log('Full URL:', (error.config?.baseURL ?? '') + (error.config?.url ?? ''));
      console.log('Authorization header:', error.config?.headers?.Authorization ?? '(not present)');
      console.log('Response status:', status);
      console.log('Response body:', error.response?.data);
      console.log('VITE_DEV_SKIP_AUTH:', import.meta.env.VITE_DEV_SKIP_AUTH);
      console.groupEnd();
      handleUnauthorized();
    } else if (status === 403) {
      handleForbidden();
    }
    return Promise.reject(error);
  }
);

export type { AxiosError, AxiosRequestConfig };
export default apiClient;
