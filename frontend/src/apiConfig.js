/**
 * API origin with no trailing slash.
 * - Local dev: leave VITE_API_BASE_URL unset → '' (`/api` proxied via vite.config → :8000).
 * - Vercel: omit VITE_* and use `vercel.json` rewrite so `/api` → Render (no CORS). Or set
 *   VITE_API_BASE_URL=https://….onrender.com and allow that origin on the backend CORS_ORIGINS / regex.
 */
export function getApiBase() {
  const raw = import.meta.env.VITE_API_BASE_URL;
  if (raw == null || String(raw).trim() === '') return '';
  return String(raw).trim().replace(/\/$/, '');
}
