import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  base: '/app/',   // <-- Add this

  plugins: [react()],

  resolve: {
    alias: {
      app: path.resolve(__dirname, 'src/app'),
      features: path.resolve(__dirname, 'src/features'),
      shared: path.resolve(__dirname, 'src/shared'),
      config: path.resolve(__dirname, 'src/config'),
      assets: path.resolve(__dirname, 'src/assets'),
      styles: path.resolve(__dirname, 'src/styles'),
      types: path.resolve(__dirname, 'src/types'),
      utils: path.resolve(__dirname, 'src/utils'),
      hooks: path.resolve(__dirname, 'src/hooks'),
      constants: path.resolve(__dirname, 'src/constants'),
      contexts: path.resolve(__dirname, 'src/contexts'),
      pages: path.resolve(__dirname, 'src/pages'),
      routes: path.resolve(__dirname, 'src/routes'),
      services: path.resolve(__dirname, 'src/services'),
      store: path.resolve(__dirname, 'src/store'),
    },
  },

  server: {
    port: 3000,
    open: true,
  },

  build: {
    outDir: 'build',
    sourcemap: false,
  },
});