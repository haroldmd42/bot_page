import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Use relative base path for seamless GitHub Pages subpath deployment
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  }
});
