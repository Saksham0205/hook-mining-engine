/**
 * API origin with no trailing slash.
 * - Local dev: leave VITE_API_BASE_URL unset → '' so requests use `/api` and Vite proxies to :8000.
 * - Vercel: set VITE_API_BASE_URL=https://your-backend.onrender.com
 */
export function getApiBase() {
  const raw = import.meta.env.VITE_API_BASE_URL;
  if (raw == null || String(raw).trim() === '') return '';
  return String(raw).trim().replace(/\/$/, '');
}
