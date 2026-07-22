import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';
import { apiBaseUrl, apiTimeout } from 'config/env';
import { handleForbidden, handleUnauthorized } from 'utils/sessionLifecycle';

export const apiClient: AxiosInstance = axios.create({
  baseURL: 'https://suraksha-iq-backend-docker-50044197283.development.catalystappsail.in/api/v1/auth/login',
  timeout: apiTimeout,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (typeof localStorage !== 'undefined' && config.headers) {
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
      handleUnauthorized();
    } else if (status === 403) {
      handleForbidden();
    }
    return Promise.reject(error);
  }
);

export type { AxiosError, AxiosRequestConfig };
export default apiClient;
