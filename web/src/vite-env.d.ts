/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FUNCTIONS_ORIGIN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
