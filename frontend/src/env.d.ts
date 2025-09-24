/// <reference types="vite/client" />
/// <reference types="unplugin-vue-router/client" />

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  readonly VITE_API_BASE_URL: string
  readonly VITE_BACKEND_ENDPOINT: string
  readonly VITE_OSS_ENDPOINT: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
