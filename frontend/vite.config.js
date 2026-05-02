import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  // Set during `vite build` on Vercel (VERCEL=1). Used to prefer same-origin /api (vercel.json proxy).
  define: {
    'import.meta.env.VITE_IS_VERCEL_BUILD': JSON.stringify(process.env.VERCEL === '1' ? '1' : ''),
  },
  plugins: [react()],
  server: {
    // `/api/*` stays same-origin in dev while `npm run dev` proxies to backend (see `.env`/apiConfig.js for prod URL).
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});
