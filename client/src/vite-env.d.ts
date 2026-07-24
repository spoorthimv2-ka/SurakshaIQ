/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_API_TIMEOUT: string;
  readonly VITE_BUILD_VERSION: string;
  readonly VITE_APP_NAME: string;
  readonly VITE_ENVIRONMENT: string;
  readonly VITE_BASE_PATH: string;
  readonly VITE_DEV_SKIP_AUTH: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
