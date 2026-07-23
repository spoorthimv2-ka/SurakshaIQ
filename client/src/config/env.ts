export const apiBaseUrl =
  import.meta.env.VITE_API_URL ??
  "https://suraksha-iq-backend-docker-50044292645.development.catalystappsail.in/api/v1";

export const apiTimeout = import.meta.env.VITE_API_TIMEOUT
  ? parseInt(import.meta.env.VITE_API_TIMEOUT, 10)
  : 30000;

export const buildVersion = import.meta.env.VITE_BUILD_VERSION || '1.0.0';

export const appName = import.meta.env.VITE_APP_NAME || 'SurakshaIQ';

export const environment = import.meta.env.VITE_ENVIRONMENT || 'development';
