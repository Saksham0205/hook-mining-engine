import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    // `/api/*` stays same-origin in dev while `npm run dev` proxies to backend (see `.env`/apiConfig.js for prod URL).
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});
