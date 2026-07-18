/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_GATEWAY_URL: string;
  readonly VITE_API_TIMEOUT: string;
  readonly VITE_ENABLE_MOCK_MODE: string;
  readonly VITE_BUILD_VERSION: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
