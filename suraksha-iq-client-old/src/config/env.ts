export const apiGatewayUrl =
  import.meta.env.VITE_API_GATEWAY_URL || 'http://localhost:3001';

export const apiTimeout = import.meta.env.VITE_API_TIMEOUT
  ? parseInt(import.meta.env.VITE_API_TIMEOUT, 10)
  : 30000;

export const enableMockMode =
  import.meta.env.VITE_ENABLE_MOCK_MODE === 'true';

export const buildVersion =
  import.meta.env.VITE_BUILD_VERSION || '1.0.0';
